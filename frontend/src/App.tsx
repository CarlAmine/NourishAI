import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Navbar } from '@/components/Navbar'
import { Home } from '@/pages/Home'
import { RecipeSearch } from '@/pages/RecipeSearch'
import { RecipeRecommender } from '@/pages/RecipeRecommender'
import { MealPlanPage } from '@/pages/MealPlan'
import { NutritionTracker } from '@/pages/NutritionTracker'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-cream-50">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/search" element={<RecipeSearch />} />
            <Route path="/recommend" element={<RecipeRecommender />} />
            <Route path="/meal-plan" element={<MealPlanPage />} />
            <Route path="/nutrition" element={<NutritionTracker />} />
          </Routes>
        </main>
        <div className="grain-overlay" />
      </div>
    </Router>
  )
}

export default App
