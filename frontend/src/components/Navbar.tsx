import { Link, useLocation } from 'react-router-dom';
import { Leaf, Search, Sparkles, CalendarDays, BarChart3 } from 'lucide-react';

const links = [
  { to: '/', label: 'Home', icon: Leaf },
  { to: '/search', label: 'Search', icon: Search },
  { to: '/recommend', label: 'Recommend', icon: Sparkles },
  { to: '/meal-plan', label: 'Meal Plan', icon: CalendarDays },
  { to: '/nutrition', label: 'Nutrition', icon: BarChart3 },
];

export default function Navbar() {
  const { pathname } = useLocation();
  return (
    <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur border-b border-stone-200 shadow-sm">
      <div className="max-w-6xl mx-auto px-4 flex items-center justify-between h-16">
        <Link to="/" className="flex items-center gap-2 font-bold text-xl text-forest-700">
          <Leaf className="text-forest-500" size={22} />
          NourishAI
        </Link>
        <div className="flex items-center gap-1">
          {links.map(({ to, label, icon: Icon }) => (
            <Link
              key={to}
              to={to}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                pathname === to
                  ? 'bg-forest-100 text-forest-700'
                  : 'text-stone-600 hover:bg-stone-100'
              }`}
            >
              <Icon size={16} />
              <span className="hidden sm:inline">{label}</span>
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
