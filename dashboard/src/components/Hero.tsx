import React from 'react';

const Hero: React.FC = () => {
  return (
    <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">
          Beyond Vanta: Real-time GDPR compliance for modern SaaS
        </h1>
        <p className="text-xl sm:text-2xl text-blue-100 mb-8">
          Automated cookie consent monitoring that developers actually want to use
        </p>
        <div className="flex justify-center space-x-4">
          <button className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors">
            Join Waitlist
          </button>
          <button className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white/10 transition-colors">
            View Demo
          </button>
        </div>
      </div>
    </div>
  );
};

export default Hero; 