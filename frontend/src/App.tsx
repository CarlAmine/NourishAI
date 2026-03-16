import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import RecipeSearch from './pages/RecipeSearch';
import RecipeRecommender from './pages/RecipeRecommender';
import MealPlan from './pages/MealPlan';
import NutritionTracker from './pages/NutritionTracker';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-stone-50">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/search" element={<RecipeSearch />} />
            <Route path="/recommend" element={<RecipeRecommender />} />
            <Route path="/meal-plan" element={<MealPlan />} />
            <Route path="/nutrition" element={<NutritionTracker />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
