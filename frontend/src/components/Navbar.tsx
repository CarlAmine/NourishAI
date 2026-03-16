import { Link, useLocation } from 'react-router-dom'
import { Leaf, Search, Zap, Calendar, BarChart3 } from 'lucide-react'

export function Navbar() {
  const location = useLocation()

  const links = [
    { path: '/', label: 'Home', icon: Leaf },
    { path: '/search', label: 'Search', icon: Search },
    { path: '/recommend', label: 'Recommend', icon: Zap },
    { path: '/meal-plan', label: 'Meal Plan', icon: Calendar },
    { path: '/nutrition', label: 'Nutrition', icon: BarChart3 },
  ]

  return (
    <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-cream-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 bg-gradient-to-br from-forest-500 to-forest-600 rounded-lg flex items-center justify-center">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <span className="font-display text-xl font-bold text-forest-700 group-hover:text-forest-600 transition-colors">
              NourishAI
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-1">
            {links.map(({ path, label, icon: Icon }) => {
              const isActive = location.pathname === path
              return (
                <Link
                  key={path}
                  to={path}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-forest-50 text-forest-700 font-medium'
                      : 'text-charcoal-700 hover:bg-cream-100'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="text-sm">{label}</span>
                </Link>
              )
            })}
          </div>

          <div className="md:hidden flex items-center gap-2">
            <div className="flex gap-1">
              {links.map(({ path, icon: Icon }) => {
                const isActive = location.pathname === path
                return (
                  <Link
                    key={path}
                    to={path}
                    className={`p-2 rounded-lg transition-all duration-200 ${
                      isActive ? 'bg-forest-50 text-forest-700' : 'text-charcoal-700 hover:bg-cream-100'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </Link>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}
