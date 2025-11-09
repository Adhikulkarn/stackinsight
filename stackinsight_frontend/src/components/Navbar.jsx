import { motion } from "framer-motion";

export default function Navbar() {
  return (
    <motion.nav
      initial={{ y: -40, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6 }}
      className="fixed top-0 left-0 w-full backdrop-blur-md bg-white/10 border-b border-gray-800 z-50"
    >
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <h1 className="text-2xl font-extrabold text-white tracking-wide">
          Stack<span className="text-cyan-400">Insight</span>
        </h1>
        <div className="space-x-6 text-gray-300 text-sm font-medium hidden md:flex">
          <a href="#features" className="hover:text-cyan-400 transition">Features</a>
          <a href="#api" className="hover:text-cyan-400 transition">API</a>
          <a href="#about" className="hover:text-cyan-400 transition">About</a>
          <a href="#contact" className="hover:text-cyan-400 transition">Contact</a>
        </div>
      </div>
    </motion.nav>
  );
}
