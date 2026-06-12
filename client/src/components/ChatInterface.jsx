import { useState, useRef, useEffect } from 'react';
import { Mic, Paperclip, Send } from 'lucide-react';
import MessageBubble from './MessageBubble';
import { getMockResponse, MOCK_PROMPT } from '../MockResponse';
import { motion, AnimatePresence } from 'framer-motion';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';

export default function ChatInterface({ messages, setMessages, setCurrentContext }) {
  const [input, setInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    const tempAssistantMessage = { role: 'assistant', content: 'Analyzing multi-hop causal chains...', isLoading: true };
    setMessages(prev => [...prev, tempAssistantMessage]);

    try {
      let data;
      const USE_MOCK = false;

      if (USE_MOCK) {
        data = await getMockResponse();
      } else {
        const response = await fetch(`${BACKEND_URL}/api/query`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: userMessage.content })
        });
        data = await response.json();
      }

      setMessages(prev => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = {
          role: 'assistant',
          content: data.answer
        };
        return newMessages;
      });
      setCurrentContext(data.context);
    } catch (error) {
      console.error(error);
    }
  };

  const setMockPrompt = () => setInput(MOCK_PROMPT);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    const systemMessage = { role: 'system', content: `Ingesting file: ${file.name}...` };
    setMessages(prev => [...prev, systemMessage]);

    try {
      const response = await fetch(`${BACKEND_URL}/api/upload`, {
        method: 'POST',
        body: formData
      });
      await response.json();

      setMessages(prev => [...prev, { role: 'system', content: `File ingested into Knowledge Base: ${file.name}` }]);
    } catch (error) {
      console.error("Upload error:", error);
      setMessages(prev => [...prev, { role: 'system', content: `Failed to ingest file: ${file.name}` }]);
    }
  };

  const toggleRecording = async () => {
    if (isRecording) {
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };

        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          const formData = new FormData();
          formData.append('file', audioBlob, 'recording.webm');

          setMessages(prev => [...prev, { role: 'system', content: `Ingesting audio recording...` }]);

          try {
            const response = await fetch(`${BACKEND_URL}/api/upload`, {
              method: 'POST',
              body: formData
            });
            await response.json();
            setMessages(prev => [...prev, { role: 'system', content: `Audio ingested into Knowledge Base.` }]);
          } catch (error) {
            console.error("Audio upload error:", error);
            setMessages(prev => [...prev, { role: 'system', content: `Failed to ingest audio.` }]);
          }

          stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        setIsRecording(true);
      } catch (err) {
        console.error("Microphone access denied:", err);
        alert("Could not access microphone.");
      }
    }
  };

  return (
    <div className="flex flex-col h-full relative px-6 md:px-12 pt-24 pb-8">
      {messages.length === 0 && (
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none opacity-40">
          <h1 className="text-4xl font-bold tracking-tighter mb-2">GraphRAG Nexus</h1>
          <p className="text-text-muted">Ask anything about the knowledge base.</p>
        </div>
      )}

      <div className="flex-1 overflow-y-auto space-y-8 scroll-smooth no-scrollbar relative z-10">
        <AnimatePresence>
          {messages.map((msg, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20, filter: 'blur(5px)' }}
              animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
              transition={{ duration: 0.6, ease: [0.32, 0.72, 0, 1] }}
            >
              <MessageBubble message={msg} />
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef} className="h-4" />
      </div>

      <div className="mt-6 relative z-20">
        {/* Double-Bezel Nested Architecture Input */}
        <div className="p-1.5 rounded-[2rem] glass-panel glass-inner">
          <div className="flex items-end gap-2 bg-surface-elevated/80 border border-border-subtle rounded-[calc(2rem-0.375rem)] px-4 py-3 shadow-[inset_0_1px_1px_rgba(255,255,255,0.8)] dark:shadow-[inset_0_1px_1px_rgba(255,255,255,0.02)]">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-2 text-text-muted hover:text-text-primary transition-all rounded-full hover:bg-border-subtle active:scale-[0.98]"
            >
              <Paperclip size={20} />
            </button>
            <input type="file" ref={fileInputRef} className="hidden" onChange={handleFileUpload} />

            <button
              onClick={toggleRecording}
              className={`p-2 transition-all rounded-full hover:bg-border-subtle active:scale-[0.98] ${isRecording ? 'text-red-500 animate-pulse' : 'text-text-muted hover:text-text-primary'}`}
            >
              <Mic size={20} />
            </button>

            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Ask anything..."
              className="flex-1 bg-transparent border-none outline-none resize-none max-h-32 min-h-[24px] p-2 text-text-primary placeholder:text-text-muted/50 font-medium"
              rows={1}
            />

            <button
              onClick={handleSend}
              disabled={!input.trim()}
              className="p-3 bg-text-primary text-surface-elevated rounded-full hover:scale-[1.02] active:scale-[0.98] disabled:opacity-30 disabled:hover:scale-100 transition-all ml-2"
            >
              <Send size={18} className="translate-x-[1px] -translate-y-[1px]" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
