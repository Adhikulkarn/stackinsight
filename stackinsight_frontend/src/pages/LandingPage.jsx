import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import { FaGithub, FaCode, FaChartLine, FaRocket, FaBrain, FaArrowRight } from "react-icons/fa";

const Navbar = () => (
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
        <a href="#how-it-works" className="hover:text-cyan-400 transition">How It Works</a>
        <a href="#analyze" className="hover:text-cyan-400 transition">Get Started</a>
        <a href="https://github.com/Adhikulkarn" target="_blank" rel="noopener noreferrer" className="hover:text-cyan-400 transition">GitHub</a>
      </div>
    </div>
  </motion.nav>
);

const FeatureCard = ({ icon, title, description, delay }) => (
  <motion.div
    initial={{ opacity: 0, y: 30 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ delay, duration: 0.6 }}
    whileHover={{ y: -10, scale: 1.02 }}
    className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-sm p-8 rounded-2xl border border-gray-700/50 hover:border-cyan-500/50 transition-all duration-300 group"
  >
    <div className="text-4xl mb-4 text-cyan-400 group-hover:scale-110 transition-transform">
      {icon}
    </div>
    <h3 className="text-xl font-bold mb-3 text-white">{title}</h3>
    <p className="text-gray-400 leading-relaxed">{description}</p>
  </motion.div>
);

const StatsCounter = ({ end, label, suffix = "" }) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const duration = 2000;
    const steps = 60;
    const increment = end / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(Math.floor(current));
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [end]);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.5 }}
      whileInView={{ opacity: 1, scale: 1 }}
      viewport={{ once: true }}
      className="text-center"
    >
      <div className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-cyan-400 to-blue-600 text-transparent bg-clip-text mb-2">
        {count}{suffix}
      </div>
      <div className="text-gray-400 text-sm">{label}</div>
    </motion.div>
  );
};

export default function LandingPage() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  return (
    <div className="landing-page">
      {/* Animated cursor glow */}
      <div
        className="cursor-glow"
        style={{
          background: `radial-gradient(600px at ${mousePosition.x}px ${mousePosition.y}px, rgba(34, 211, 238, 0.15), transparent 80%)`,
        }}
      />

      <Navbar />

      {/* Hero Section */}
      <section className="hero-section">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8 }}
          className="mb-6"
        >
          <span className="hero-badge">
            🚀 AI-Powered Repository Analysis
          </span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="hero-title"
        >
          Understand Code<br />in Seconds
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.8 }}
          className="hero-description"
        >
          Transform any GitHub repository into actionable insights with AI-powered analysis, 
          visualization, and intelligent summaries.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7, duration: 0.8 }}
          className="hero-buttons"
        >
          <a href="#analyze" className="btn-primary group">
            Start Analyzing
            <FaArrowRight className="ml-2 group-hover:translate-x-1 transition-transform" />
          </a>
          <a
            href="https://github.com/Adhikulkarn"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary"
          >
            <FaGithub className="text-2xl mr-2" /> View Source
          </a>
        </motion.div>

        {/* Stats */}
        <div className="stats-grid">
          <StatsCounter end={10000} label="Repos Analyzed" suffix="+" />
          <StatsCounter end={50000} label="Lines of Code" suffix="+" />
          <StatsCounter end={99} label="Accuracy Rate" suffix="%" />
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="how-it-works-section">
        <div className="max-w-5xl mx-auto text-center">
          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="section-title"
          >
            How It Works
          </motion.h2>

          <div className="grid md:grid-cols-3 gap-12">
            {[
              { num: "01", title: "Paste URL", desc: "Simply paste any GitHub repository URL" },
              { num: "02", title: "AI Analyzes", desc: "Our AI processes and understands the codebase" },
              { num: "03", title: "Get Insights", desc: "Receive comprehensive analysis and visualizations" }
            ].map((step, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.2 }}
                className="step-card"
              >
                <div className="step-number">{step.num}</div>
                <h3 className="step-title">{step.title}</h3>
                <p className="step-description">{step.desc}</p>
                {i < 2 && (
                  <div className="step-arrow">→</div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section id="analyze" className="cta-section">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="cta-container"
        >
          <h2 className="cta-title">
            Ready to Analyze Your First Repo?
          </h2>
          <p className="cta-description">
            Join the smart developers who use StackInsight to understand code faster
          </p>
          <a href="/analyze" className="cta-button">
            Get Started Free
          </a>
        </motion.div>
      </section>

      {/* Decorative Elements */}
      <div className="blur-decoration blur-cyan"></div>
      <div className="blur-decoration blur-blue"></div>
      <div className="blur-decoration blur-purple"></div>

      {/* Floating particles */}
      {[...Array(20)].map((_, i) => (
        <motion.div
          key={i}
          className="floating-particle"
          animate={{
            y: [0, -100, 0],
            x: [0, Math.random() * 100 - 50, 0],
            opacity: [0.2, 0.5, 0.2],
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: Math.random() * 2,
          }}
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
        />
      ))}
    </div>
  );
}