import { Link } from 'react-router-dom'
import { Search, Zap, Calendar, BarChart3, Leaf, ArrowRight } from 'lucide-react'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

export function Home() {
  const [healthStatus, setHealthStatus] = useState<boolean | null>(null)

  useEffect(() => {
    api
      .healthCheck()
      .then(() => setHealthStatus(true))
      .catch(() => setHealthStatus(false))
  }, [])

  const features = [
    {
      icon: Search,
      title: 'Smart Recipe Search',
      description: 'Find recipes using semantic search with advanced filtering and reranking.',
      path: '/search',
      color: 'from-forest-500 to-forest-600',
    },
    {
      icon: Zap,
      title: 'AI Recommendations',
      description: 'Get personalized recipe suggestions based on available ingredients.',
      path: '/recommend',
      color: 'from-terracotta-500 to-terracotta-600',
    },
    {
      icon: Calendar,
      title: 'Meal Planning',
      description: 'Plan your weekly meals with AI-generated meal plans.',
      path: '/meal-plan',
      color: 'from-forest-400 to-forest-500',
    },
    {
      icon: BarChart3,
      title: 'Nutrition Tracking',
      description: 'Monitor your daily nutrition with detailed macro breakdowns.',
      path: '/nutrition',
      color: 'from-terracotta-400 to-terracotta-500',
    },
  ]

  return (
    <div className="min-h-screen">
      <section className="relative pt-20 pb-32 px-4 sm:px-6 lg:px-8 overflow-hidden">
        <div className="absolute inset-0 -z-10 bg-lines opacity-50"></div>
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 mb-6 px-4 py-2 bg-forest-50 rounded-full border border-forest-200">
            <Leaf className="w-4 h-4 text-forest-600" />
            <span className="text-sm font-medium text-forest-700">AI-Powered Nutrition</span>
          </div>

          <h1 className="font-display text-5xl md:text-6xl font-bold text-charcoal-900 mb-6 leading-tight">
            Nourish Your Body with{' '}
            <span className="bg-gradient-to-r from-forest-600 to-terracotta-500 bg-clip-text text-transparent">
              AI Intelligence
            </span>
          </h1>

          <p className="text-lg md:text-xl text-charcoal-700 mb-8 max-w-2xl mx-auto leading-relaxed">
            Discover personalized recipes, plan your meals intelligently, and track your nutrition with cutting-edge AI recommendations.
          </p>

          <div className="flex items-center justify-center gap-2 mb-12">
            <div className={`w-3 h-3 rounded-full ${
              healthStatus === true ? 'bg-forest-500' : healthStatus === false ? 'bg-terracotta-500' : 'bg-cream-300'
            }`}></div>
            <span className="text-sm text-charcoal-700/70">
              {healthStatus === true && 'Backend connected'}
              {healthStatus === false && 'Backend unavailable'}
              {healthStatus === null && 'Checking connection...'}
            </span>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/search" className="btn-primary">
              <Search className="w-5 h-5" />
              Start Searching
            </Link>
            <Link to="/recommend" className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-cream-200 text-charcoal-800 font-medium rounded-xl hover:bg-cream-300 transition-all duration-200">
              <Zap className="w-5 h-5" />
              Get Recommendations
            </Link>
          </div>
        </div>
      </section>

      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-transparent to-cream-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-display text-3xl md:text-4xl font-bold text-charcoal-900 mb-4">Everything You Need</h2>
            <p className="text-lg text-charcoal-700/70 max-w-2xl mx-auto">Comprehensive tools to help you make better nutritional choices every day.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feature) => {
              const Icon = feature.icon
              return (
                <Link key={feature.path} to={feature.path} className="group card p-8 hover:shadow-lg transition-all duration-300">
                  <div className="flex items-start justify-between mb-6">
                    <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}>
                      <Icon className="w-7 h-7 text-white" />
                    </div>
                    <ArrowRight className="w-5 h-5 text-charcoal-700/30 group-hover:text-forest-600 group-hover:translate-x-1 transition-all duration-300" />
                  </div>
                  <h3 className="font-display text-xl font-bold text-charcoal-900 mb-3 group-hover:text-forest-600 transition-colors">{feature.title}</h3>
                  <p className="text-charcoal-700/70 leading-relaxed">{feature.description}</p>
                </Link>
              )
            })}
          </div>
        </div>
      </section>

      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="font-display text-3xl font-bold text-charcoal-900 mb-6">Ready to transform your nutrition?</h2>
          <p className="text-lg text-charcoal-700/70 mb-8">Start exploring recipes and meal plans powered by AI today.</p>
          <Link to="/search" className="btn-primary inline-flex items-center gap-2">
            <Search className="w-5 h-5" />
            Explore Now
          </Link>
        </div>
      </section>
    </div>
  )
}
