import os
import json
from typing import List

from ollama import Client
from moviepy import VideoFileClip
from models.GraphModels import Node, Edge, KnowledgeGraph
from config.Config import OLLAMA_BASE_URL, OLLAMA_MODEL

# Import existing encoders 
from services.encoders.Encoder import ImageOCRModel
from services.encoders.PDFProcessor import PDFProcessor

# For Audio/Video processing
from transformers import pipeline

class EntityRelationExtractor:
    def __init__(self):
        self.ollama_client = Client(host=OLLAMA_BASE_URL)
        self.model_name = OLLAMA_MODEL
        
        self.pdf_processor = PDFProcessor()
        self.ocr_model = ImageOCRModel(device="cpu")
        # Lazy-loaded whisper model for CPU efficiency
        self.speech_recognizer = None
        
        # Lazy-loaded BLIP image captioner
        self.captioner = None

    def _get_captioner(self):
        """Lazy load the BLIP pipeline for visual semantics."""
        if self.captioner is None:
            print("Loading CPU-friendly BLIP image captioner...")
            self.captioner = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base", device="cpu")
        return self.captioner

    def _get_file_type(self, file_path: str) -> str:
        """Helper to determine modality from file extension."""
        if len(file_path) > 255 or not os.path.isfile(file_path):
            return "raw_text"
        ext = file_path.split('.')[-1].lower()
        if ext == "pdf": return "pdf"
        elif ext in ["png", "jpg", "jpeg", "gif", "webp"]: return "image"
        elif ext in ["wav", "mp3", "flac", "aac", "m4a"]: return "audio"
        elif ext in ["mp4", "avi", "mkv", "mov", "wmv"]: return "video"
        elif ext == "txt": return "text_file"
        return "raw_text"

    def _get_whisper_pipeline(self):
        """Lazy load the Whisper pipeline so it doesn't consume memory if only doing text/image."""
        if self.speech_recognizer is None:
            print("Loading CPU-friendly Whisper-tiny model for audio transcription...")
            # Use 'openai/whisper-tiny' as it is highly CPU efficient and accurate enough for entity extraction
            self.speech_recognizer = pipeline(
                "automatic-speech-recognition",
                model="openai/whisper-tiny",
                device="cpu" 
            )
        return self.speech_recognizer

    def extract_text_from_audio(self, audio_path: str) -> str:
        """Extracts text transcript from an audio file."""
        recognizer = self._get_whisper_pipeline()
        # chunk_length_s handles long audio files natively
        result = recognizer(audio_path, chunk_length_s=30)
        return result.get("text", "")

    def extract_text_from_video(self, video_path: str) -> str:
        """Extracts text transcript from a video file by pulling audio first."""
        try:
            temp_audio_path = f"{video_path}_temp.wav"
            
            # Extract audio from video if it exists
            video = VideoFileClip(video_path)
            if video.audio:
                video.audio.write_audiofile(temp_audio_path, verbose=False, logger=None)
                # Transcribe the extracted audio
                transcript = self.extract_text_from_audio(temp_audio_path)
            else:
                transcript = ""
            
            # Close the video to release file handles
            video.close()
            
            # Cleanup temporary wav file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
                
            return transcript
        except Exception as e:
            print(f"Error processing video {video_path}: {e}")
            return ""

    def translate_to_text(self, file_path: str) -> dict:
        """
        Converts the multimodal file into a dictionary of text chunks and media paths.
        """
        file_type = self._get_file_type(file_path)
        
        if file_type == "raw_text":
            return {"text": [c.strip() for c in file_path.split('\n\n') if c.strip()], "media": []}
            
        elif file_type == "text_file":
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"text": [c.strip() for c in content.split('\n\n') if c.strip()], "media": []}
            
        elif file_type == "pdf":
            chunks, images = self.pdf_processor.process_pdfFile(file_path)
            return {"text": [chunk["text"] for chunk in chunks], "media": images}
            
        elif file_type == "image":
            ocr_text = self.ocr_model.extract_text(file_path)
            
            try:
                captioner = self._get_captioner()
                caption_result = captioner(file_path)
                visual_caption = caption_result[0].get("generated_text", "").strip() if caption_result else ""
            except Exception as e:
                print(f"BLIP Captioning Failed on {file_path}: {e}")
                visual_caption = ""
                
            final_text = []
            if visual_caption:
                final_text.append(f"[Visual Description]: {visual_caption.capitalize()}")
            if ocr_text:
                final_text.append(f"[Text found in image]: {ocr_text}")
                
            combined_text = " ".join(final_text)
            return {"text": [combined_text] if combined_text else [], "media": [file_path]}
            
        elif file_type == "audio":
            text = self.extract_text_from_audio(file_path)
            return {"text": [text] if text else [], "media": []}
            
        elif file_type == "video":
            text = self.extract_text_from_video(file_path)
            return {"text": [text] if text else [], "media": []}

        return {"text": [], "media": []}

    def extract_graph(self, file_path: str, text_chunks: List[str] = None) -> KnowledgeGraph:
        """
        Main entry point. Uses existing text chunks to generate Graph Nodes/Edges via Ollama.
        """
        if text_chunks is None:
            print(f"Translating {file_path} to textual content...")
            extraction = self.translate_to_text(file_path)
            text_chunks = extraction["text"]
        
        if not text_chunks:
            print("No text could be extracted from the file.")
            return KnowledgeGraph(nodes=[], edges=[])

        all_nodes = {}
        all_edges = []
        
        print(f"Extracted {len(text_chunks)} text chunk(s). Running LLM Entity Extraction with Ollama...")
        
        for idx, chunk in enumerate(text_chunks):
            if not chunk.strip():
                continue
                
            print(f"  -> Processing chunk {idx + 1}/{len(text_chunks)}")
            
            prompt = (
                "Perform Named Entity Recognition (NER) and extract knowledge graph triplets from the text. "
                "You must output the extracted data strictly in the requested JSON format containing 'nodes' and 'edges'.\n\n"
                "**Entity Types:**\n"
                '["PERSON", "ORGANIZATION", "LOCATION", "CONCEPT", "EVENT", "DATE", "PRODUCT", "TECHNOLOGY", "OTHER"]\n\n'
                "**Predicates:**\n"
                '["IS_A", "PART_OF", "LOCATED_IN", "WORKS_FOR", "OWNED_BY", "RELATED_TO", "HAS_ATTRIBUTE", "CAUSES", "PREVENTS", "ENABLES", "RESULTS_IN", "PARTICIPATES_IN", "USES", "CREATED_BY"]\n\n'
                "CRITICAL INSTRUCTION: Aggressively hunt for causal relationships in the text. Whenever action A leads to event B, you MUST use one of the causal predicates: 'CAUSES', 'PREVENTS', 'ENABLES', or 'RESULTS_IN'.\n"
                "For each node, provide a unique ID (no spaces), a display name, the entity type from the list above, and a brief description based on the text.\n"
                "For each edge, provide the source_node_id, target_node_id, the relationship_name from the predicates list, and a brief description.\n\n"
                f"**Text:**\n{chunk}"
            )
            
            try:
                response = self.ollama_client.chat(
                    model=self.model_name,
                    messages=[{'role': 'user', 'content': prompt}],
                    format=KnowledgeGraph.model_json_schema(),
                    options={'temperature': 0.0}  # Deterministic extraction
                )
                
                json_response = response['message']['content']
                parsed_graph = KnowledgeGraph(**json.loads(json_response))
                
                # Deduplicate nodes globally across all chunks
                for node in parsed_graph.nodes:
                    all_nodes[node.id] = node
                all_edges.extend(parsed_graph.edges)
                
            except Exception as e:
                print(f"Error during Ollama extraction on chunk {idx + 1}: {e}")
        
        # Stamp source type
        final_nodes = list(all_nodes.values())
        file_type = self._get_file_type(file_path)
        for node in final_nodes:
            node.source_type = file_type
        for edge in all_edges:
            edge.source_type = file_type
            
        return KnowledgeGraph(nodes=final_nodes, edges=all_edges)
