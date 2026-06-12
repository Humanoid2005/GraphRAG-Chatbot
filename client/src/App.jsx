import { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import Sidebar from './components/Sidebar';
import { Sun, Moon } from 'lucide-react';
import { motion } from 'framer-motion';

function App() {
  const [messages, setMessages] = useState([]);
  const [currentContext, setCurrentContext] = useState(null);
  const [theme, setTheme] = useState('light');

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  return (
    <div className="flex h-[100dvh] bg-bg-base text-text-primary overflow-hidden transition-colors duration-500">
      
      <button 
        onClick={toggleTheme}
        className="absolute top-6 left-6 z-50 p-3 rounded-full glass-panel text-text-muted hover:text-text-primary transition-all active:scale-[0.98]"
        title="Toggle Theme"
      >
        {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
      </button>

      <motion.div 
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.8, ease: [0.32, 0.72, 0, 1] }}
        className="w-full md:w-[70%] h-full z-10"
      >
        <ChatInterface 
          messages={messages} 
          setMessages={setMessages} 
          setCurrentContext={setCurrentContext} 
        />
      </motion.div>
      
      <motion.div 
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.8, delay: 0.1, ease: [0.32, 0.72, 0, 1] }}
        className="hidden md:block md:w-[30%] h-full z-20 border-l border-border-subtle shadow-[-20px_0_40px_rgba(0,0,0,0.03)] dark:shadow-[-20px_0_40px_rgba(0,0,0,0.3)] relative"
      >
        <Sidebar context={currentContext} />
      </motion.div>
    </div>
  );
}

export default App;
