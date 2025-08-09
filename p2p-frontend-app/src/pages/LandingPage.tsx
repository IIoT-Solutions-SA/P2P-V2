import { useNavigate } from 'react-router-dom'
import { Button } from "@/components/ui/button"
import { ArrowRight, Users, BookOpen, TrendingUp, Star, Sparkles, Globe, Building2, Cog, BarChart3, Factory, Wrench, CheckCircle, MapPin } from "lucide-react"
import InteractiveMap from "@/components/InteractiveMap"
import { SaudiRiyalCurrency } from "@/components/SaudiRiyal"

export default function LandingPage() {
  const navigate = useNavigate()
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">

      {/* Hero Section with Video Background */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Video Background */}
        <div className="absolute inset-0 w-full h-full">
          <video
            autoPlay
            muted
            loop
            playsInline
            className="w-full h-full object-cover"
          >
            <source src="/Video_Redo_Realistic_Technology.mp4" type="video/mp4" />
            Your browser does not support the video tag.
          </video>
          {/* Dark overlay for better text readability */}
          <div className="absolute inset-0 bg-slate-900/60"></div>
        </div>

        {/* Hero Content */}
        <div className="relative z-10 container mx-auto px-6 py-24">
          <div className="text-center space-y-10">
            <h1 className="text-6xl font-bold leading-tight text-white">
              Accelerate Your Factory's
              <br />
              <span className="text-blue-400">Digital Transformation</span>
            </h1>
            <p className="text-xl text-white/90 max-w-3xl mx-auto leading-relaxed">
              Join Saudi Arabia's premier peer-to-peer platform where manufacturing executives share proven strategies and explore real implementation case studies.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
              <Button 
                size="lg" 
                className="text-lg px-10 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-lg"
                onClick={() => navigate('/use-cases')}
              >
                Explore Success Stories
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Button 
                variant="outline" 
                size="lg" 
                className="text-lg px-8 py-4 text-white border-white/30 hover:bg-white/10 backdrop-blur-sm"
                onClick={() => navigate('/forum')}
              >
                Join Discussions
              </Button>
            </div>
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
          <div className="w-6 h-10 border-2 border-white/50 rounded-full p-1">
            <div className="w-1 h-3 bg-white/70 rounded-full mx-auto animate-pulse"></div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="text-center space-y-2">
              <div className="text-4xl font-bold text-blue-600">1,200+</div>
              <div className="text-slate-600 font-medium">Connected Factories</div>
            </div>
            <div className="text-center space-y-2">
              <div className="text-4xl font-bold text-blue-600">89</div>
              <div className="text-slate-600 font-medium">Proven Use Cases</div>
            </div>
            <div className="text-center space-y-2">
              <div className="text-4xl font-bold text-blue-600"><SaudiRiyalCurrency amount="45M+" /></div>
              <div className="text-slate-600 font-medium">Cost Savings Achieved</div>
            </div>
            <div className="text-center space-y-2">
              <div className="text-4xl font-bold text-blue-600">67%</div>
              <div className="text-slate-600 font-medium">Avg. Efficiency Gain</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-6 py-24">
        <div className="text-center mb-20">
          <h2 className="text-4xl font-bold text-slate-900 mb-6">Factory Optimization Tools</h2>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">Comprehensive platform designed for factory owners, plant managers, and operations teams</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="group">
            <div className="bg-blue-600 p-6 rounded-xl mb-6 group-hover:bg-blue-700 transition-colors duration-300">
              <BookOpen className="h-10 w-10 text-white" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-3">Browse Use Cases</h3>
            <p className="text-slate-600 leading-relaxed">
              Explore real factory implementations with proven results. Find automation, quality control, and efficiency solutions that work.
            </p>
          </div>
          <div className="group">
            <div className="bg-slate-600 p-6 rounded-xl mb-6 group-hover:bg-slate-700 transition-colors duration-300">
              <Users className="h-10 w-10 text-white" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-3">Factory Network</h3>
            <p className="text-slate-600 leading-relaxed">
              Connect with factory owners across Saudi Arabia. Share challenges, solutions, and collaborate on optimization projects.
            </p>
          </div>
          <div className="group">
            <div className="bg-blue-500 p-6 rounded-xl mb-6 group-hover:bg-blue-600 transition-colors duration-300">
              <BarChart3 className="h-10 w-10 text-white" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-3">Performance Tracking</h3>
            <p className="text-slate-600 leading-relaxed">
              Monitor efficiency gains, cost savings, and operational improvements. Track your factory's optimization journey.
            </p>
          </div>
        </div>
      </section>

      {/* Interactive Map Section 1 - Main Featured Map */}
      <section className="container mx-auto px-6 py-24">
        <InteractiveMap 
          height="600px"
          title="Discover Success Stories Across Saudi Arabia"
          className="mb-16"
        />
      </section>

      {/* Featured Use Cases Section */}
      <section className="container mx-auto px-6 py-24">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-slate-900 mb-6">Featured Factory Solutions</h2>
          <p className="text-xl text-slate-600">Real implementations with measurable results</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm hover:shadow-md transition-all duration-300">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Cog className="h-6 w-6 text-white" />
              </div>
              <span className="text-sm font-medium text-blue-600 bg-blue-50 px-3 py-1 rounded-full">Factory Automation</span>
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-3">AI Quality Inspection Reduces Defects by 85%</h3>
            <p className="text-slate-600 mb-4">Advanced Manufacturing Co. implemented computer vision for automated quality control, achieving significant defect reduction.</p>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">85%</div>
                <div className="text-xs text-slate-500">Defect Reduction</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600"><SaudiRiyalCurrency amount="2.3M" /></div>
                <div className="text-xs text-slate-500">Annual Savings</div>
              </div>
            </div>
            <Button 
              variant="outline" 
              className="w-full border-slate-300 text-slate-700 hover:bg-slate-50"
              onClick={() => navigate('/use-cases/1')}
            >
              View Full Case Study
            </Button>
          </div>
          <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm hover:shadow-md transition-all duration-300">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-2 bg-slate-600 rounded-lg">
                <Wrench className="h-6 w-6 text-white" />
              </div>
              <span className="text-sm font-medium text-slate-600 bg-slate-100 px-3 py-1 rounded-full">Predictive Maintenance</span>
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-3">IoT Sensors Cut Downtime by 60%</h3>
            <p className="text-slate-600 mb-4">Gulf Plastics Industries deployed IoT-based predictive maintenance, preventing equipment failures before they occur.</p>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-slate-600">60%</div>
                <div className="text-xs text-slate-500">Downtime Reduction</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-slate-600"><SaudiRiyalCurrency amount="1.8M" /></div>
                <div className="text-xs text-slate-500">Annual Savings</div>
              </div>
            </div>
            <Button 
              variant="outline" 
              className="w-full border-slate-300 text-slate-700 hover:bg-slate-50"
              onClick={() => navigate('/use-cases/1')}
            >
              View Full Case Study
            </Button>
          </div>
        </div>
      </section>


      {/* Success Stories */}
      <section className="container mx-auto px-6 py-24">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-slate-900 mb-6">Factory Success Stories</h2>
          <p className="text-xl text-slate-600">Real results from Saudi manufacturing leaders</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            { title: "Production Optimization", desc: "Automated production line monitoring increased output efficiency across multiple facilities", metric: "45% efficiency gain", color: "blue", icon: Cog },
            { title: "Quality Improvements", desc: "Implemented smart quality control systems reducing defects and improving product standards", metric: "78% defect reduction", color: "slate", icon: CheckCircle },
            { title: "Cost Savings", desc: "Energy management and predictive maintenance programs delivered significant operational savings", metric: "3.2M saved annually", color: "blue", icon: BarChart3 }
          ].map((story, i) => {
            const IconComponent = story.icon
            return (
              <div key={i} className="group relative overflow-hidden rounded-xl bg-white p-8 shadow-sm border border-slate-200 hover:shadow-md transition-all duration-300">
                <div className={`absolute top-0 left-0 w-full h-1 ${
                  story.color === 'blue' ? 'bg-blue-600' : 'bg-slate-600'
                }`}></div>
                <div className="flex items-center space-x-2 mb-4">
                  <IconComponent className="h-5 w-5 text-blue-600" />
                  <span className="text-sm font-medium text-slate-600">Factory Success</span>
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">{story.title}</h3>
                <p className="text-slate-600 mb-6 leading-relaxed">{story.desc}</p>
                <div className={`inline-block px-4 py-2 rounded-lg ${
                  story.color === 'blue' ? 'bg-blue-600' : 'bg-slate-600'
                } text-white text-sm font-semibold`}>
                  {story.title === "Cost Savings" ? <><SaudiRiyalCurrency amount="3.2M" className="text-white" /> saved annually</> : story.metric}
                </div>
              </div>
            )
          })}
        </div>
      </section>


      {/* CTA Section */}
      <section className="bg-slate-800 text-white py-24">
        <div className="container mx-auto px-6 text-center">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-5xl font-bold mb-6">Join the Factory Network</h2>
            <p className="text-xl mb-10 text-slate-300 leading-relaxed">
              Connect with factory owners across Saudi Arabia, browse proven use cases, and optimize your operations - completely free
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white text-lg px-10 py-4 rounded-lg font-semibold">
                Start Optimizing Now
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Button size="lg" variant="outline" className="text-white border-slate-600 hover:bg-slate-700 text-lg px-8 py-4 rounded-lg">
                Browse Use Cases
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-16">
        <div className="container mx-auto px-6">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-3 mb-6">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Factory className="h-6 w-6 text-white" />
              </div>
              <span className="text-2xl font-bold text-white">
                <span className="text-blue-400">Peer</span>Link
              </span>
            </div>
            <p className="text-slate-400 mb-6 max-w-2xl mx-auto leading-relaxed">
              Factory optimization network connecting Saudi Arabian manufacturers with proven solutions and expert knowledge
            </p>
            <div className="flex items-center justify-center space-x-6 mb-8">
              <a href="#" className="text-slate-400 hover:text-blue-400 transition-colors">Privacy</a>
              <a href="#" className="text-slate-400 hover:text-blue-400 transition-colors">Terms</a>
              <a href="#" className="text-slate-400 hover:text-blue-400 transition-colors">Support</a>
              <a href="#" className="text-slate-400 hover:text-blue-400 transition-colors">Contact</a>
            </div>
            <p className="text-sm text-slate-500">
              © 2024 PeerLink. All rights reserved. Built for Saudi Arabian SMEs.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}