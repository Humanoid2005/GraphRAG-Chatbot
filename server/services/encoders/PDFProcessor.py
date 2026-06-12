import os
import pymupdf4llm

class PDFProcessor:
    def __init__(self, data_path="pdf_data"):
        self.data_path = data_path
        pass

    def create_dir(self, directory):
        os.makedirs(directory, exist_ok=True)
    
    def create(self, file_path):
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                pass
    
    def write(self, file_path, data):
        with open(file_path, 'w') as f:
            f.write(data)

    def process_pdf(self, file_path):
        """Extracts markdown and images to a local directory."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")
        
        file_name = os.path.basename(file_path)
        extracted_dir = os.path.join(self.data_path, f"{file_name}_extracted")
        self.create_dir(extracted_dir)
        
        markdown_with_assets = pymupdf4llm.to_markdown(
            doc=file_path,
            write_images=True,
            image_path=extracted_dir,
            image_format="png"
        )
        
        output_file = os.path.join(extracted_dir, 'extraction.md')
        self.create(output_file)
        self.write(output_file, markdown_with_assets)
        
    def semantic_chunk_text(self, text, chunk_size, overlap_size):
        """Helper to semantically split text by paragraphs, and sentences if needed."""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk_parts = []
        current_length = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # If a single paragraph is too large, split it by sentences
            parts = [para]
            if len(para) > chunk_size:
                parts = []
                for s in para.split('. '):
                    s = s.strip()
                    if s:
                        if not s.endswith('.'):
                            s += '.'
                        parts.append(s)
                
            for part in parts:
                part_len = len(part)
                
                # If adding this part exceeds chunk_size, save the current chunk
                if current_length + part_len > chunk_size and current_chunk_parts:
                    chunks.append('\n\n'.join(current_chunk_parts))
                    
                    # Calculate overlap by keeping parts from the end
                    overlap_parts = []
                    overlap_length = 0
                    for p in reversed(current_chunk_parts):
                        if overlap_length + len(p) <= overlap_size:
                            overlap_parts.insert(0, p)
                            overlap_length += len(p) + 2 # +2 for '\n\n' or '. ' join
                        else:
                            break
                            
                    current_chunk_parts = overlap_parts
                    current_length = overlap_length
                
                current_chunk_parts.append(part)
                current_length += part_len + 2
                
        if current_chunk_parts:
            chunks.append('\n\n'.join(current_chunk_parts))
            
        return chunks

    def chunk_data(self, file_path, chunk_size=4000, overlap_size=400):
        """
        Extracts page-aware chunks directly from the PDF and splits them into 
        semantically meaningful sub-chunks (paragraphs/sentences) without cutting words.
        Increased default chunk_size for long context text encoders.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")
        
        page_chunks = pymupdf4llm.to_markdown(
            doc=file_path,
            page_chunks=True 
        )
        
        final_chunks = []
        
        for page in page_chunks:
            text = page["text"]
            metadata = page["metadata"]
            
            # Use the semantic chunker instead of naive string slicing
            semantic_chunks = self.semantic_chunk_text(text, chunk_size, overlap_size)
            
            for chunk_text in semantic_chunks:
                final_chunks.append({
                    "text": chunk_text,
                    "metadata": metadata.copy()
                })

        images = []
        file_name = os.path.basename(file_path)
        extracted_dir = os.path.join(self.data_path, f"{file_name}_extracted")
        if os.path.exists(extracted_dir):
            for filename in os.listdir(extracted_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    images.append(os.path.join(extracted_dir, filename))

        return final_chunks, images

    def process_pdfFile(self,file_path):
        self.process_pdf(file_path)
        final_chunks,images = self.chunk_data(file_path)
        return final_chunks,images