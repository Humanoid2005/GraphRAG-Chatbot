import { Database, Network, Image as ImageIcon, FileText } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Sidebar({ context }) {
  if (!context) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-text-muted p-6 text-center">
        <Network size={48} className="mb-6 opacity-10 stroke-[1px]" />
        <h3 className="text-lg font-medium mb-2 tracking-tight">Causal Map Inactive</h3>
        <p className="text-sm max-w-[250px] leading-relaxed">The reasoning graph will materialize here once a query is executed.</p>
      </div>
    );
  }

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const item = {
    hidden: { opacity: 0, y: 10 },
    show: { opacity: 1, y: 0, transition: { ease: [0.32, 0.72, 0, 1] } }
  };

  return (
    <div className="h-full flex flex-col overflow-y-auto no-scrollbar pb-10">
      <div className="p-6 border-b border-border-subtle bg-surface-elevated/80 backdrop-blur-xl sticky top-0 z-10 flex items-center justify-between">
        <h2 className="font-semibold tracking-tight text-sm flex items-center gap-2">
          <Network size={16} className="text-accent" />
          Neural Reasoning
        </h2>
        <span className="text-[10px] uppercase tracking-widest font-bold bg-accent/10 text-accent px-2 py-0.5 rounded-full">Active</span>
      </div>

      <motion.div 
        variants={container}
        initial="hidden"
        animate="show"
        className="p-6 space-y-8"
      >
        <motion.section variants={item}>
          <h3 className="text-[10px] font-bold uppercase tracking-widest text-text-muted mb-4 flex items-center gap-2">
            <Database size={12} /> Semantic Vectors
          </h3>
          
          <div className="space-y-4">
            {context.vector_chunks?.map((chunk, idx) => (
              <div key={idx} className="glass-panel glass-inner rounded-[1.5rem] p-4 text-sm relative group overflow-hidden">
                <div className="absolute top-0 left-0 w-1 h-full bg-accent/20 group-hover:bg-accent transition-colors" />
                <div className="flex items-start gap-2 mb-2 text-text-primary">
                  <FileText size={14} className="mt-0.5 text-accent" />
                  <span className="text-[11px] font-bold uppercase tracking-wider">Chunk {idx + 1}</span>
                </div>
                <p className="text-text-muted leading-relaxed line-clamp-4">{chunk}</p>
              </div>
            ))}

            {context.vector_images?.length > 0 && (
              <div className="mt-6">
                <h4 className="text-[10px] font-bold uppercase tracking-widest text-text-muted mb-3 flex items-center gap-2">
                  <ImageIcon size={12} /> Visual Anchors
                </h4>
                <div className="grid grid-cols-2 gap-3">
                  {context.vector_images.map((img, idx) => (
                    <div key={idx} className="relative aspect-video rounded-xl overflow-hidden glass-panel glass-inner">
                      <img src={img} alt={`Context ${idx}`} className="object-cover w-full h-full opacity-80 hover:opacity-100 transition-opacity" />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </motion.section>

        <motion.section variants={item}>
          <h3 className="text-[10px] font-bold uppercase tracking-widest text-text-muted mb-4 flex items-center gap-2">
            <Network size={12} /> Causal Chains
          </h3>
          
          <div className="space-y-6">
            <div className="space-y-2">
              <h4 className="text-[10px] font-bold uppercase tracking-widest text-text-muted/70">Multi-Hop Paths</h4>
              <div className="bg-bg-base border border-accent/20 rounded-[1.5rem] p-4 text-xs font-mono text-accent overflow-x-auto shadow-[inset_0_2px_10px_rgba(0,0,0,0.02)]">
                {context.causal_chains?.map((chain, idx) => (
                  <div key={idx} className="whitespace-nowrap mb-2 last:mb-0 opacity-90">{chain}</div>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="text-[10px] font-bold uppercase tracking-widest text-text-muted/70">Graph Edges</h4>
              <div className="bg-bg-base border border-border-subtle rounded-[1.5rem] p-4 text-xs font-mono text-text-muted overflow-x-auto">
                {context.graph_relationships?.map((rel, idx) => (
                  <div key={idx} className="whitespace-nowrap mb-1 last:mb-0">{rel}</div>
                ))}
              </div>
            </div>
          </div>
        </motion.section>
      </motion.div>
    </div>
  );
}
