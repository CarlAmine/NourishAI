import { useState } from 'react';
import { Sparkles, X } from 'lucide-react';
import { api } from '../lib/api';
import type { RecipeResult } from '../types/api';
import RecipeCard from '../components/RecipeCard';
import { GridSkeleton } from '../components/SkeletonLoader';

export default function RecipeRecommender() {
  const [input, setInput] = useState('');
  const [ingredients, setIngredients] = useState<string[]>([]);
  const [dietaryNotes, setDietaryNotes] = useState('');
  const [results, setResults] = useState<RecipeResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recommended, setRecommended] = useState(false);

  const addIngredient = () => {
    const trimmed = input.trim();
    if (trimmed && !ingredients.includes(trimmed)) {
      setIngredients([...ingredients, trimmed]);
    }
    setInput('');
  };

  const handleRecommend = async () => {
    if (ingredients.length === 0) return;
    setLoading(true);
    setError(null);
    setRecommended(true);
    try {
      const data = await api.recommendRecipes({
        ingredients,
        dietary_notes: dietaryNotes || undefined,
        top_k: 9,
        rerank: true,
      });
      setResults(data.results);
    } catch {
      setError('Recommendation failed. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold text-stone-800 mb-2">AI Recommender</h1>
      <p className="text-stone-500 mb-8">Enter ingredients you have on hand and get personalized recipe ideas.</p>

      <div className="bg-white rounded-2xl border border-stone-100 shadow-sm p-6 mb-8">
        <div className="flex gap-2 mb-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && addIngredient()}
            placeholder="Add an ingredient and press Enter"
            className="flex-1 px-4 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-forest-400"
          />
          <button onClick={addIngredient} className="bg-forest-100 hover:bg-forest-200 text-forest-700 px-4 py-2.5 rounded-xl font-medium transition-colors">
            Add
          </button>
        </div>

        {ingredients.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {ingredients.map((ing) => (
              <span key={ing} className="flex items-center gap-1 bg-forest-50 text-forest-700 text-sm px-3 py-1 rounded-full">
                {ing}
                <button onClick={() => setIngredients(ingredients.filter((i) => i !== ing))}>
                  <X size={13} />
                </button>
              </span>
            ))}
          </div>
        )}

        <input
          type="text"
          value={dietaryNotes}
          onChange={(e) => setDietaryNotes(e.target.value)}
          placeholder="Dietary notes (e.g. gluten-free, high-protein, vegan)"
          className="w-full px-4 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-forest-400 mb-4"
        />

        <button
          onClick={handleRecommend}
          disabled={loading || ingredients.length === 0}
          className="flex items-center gap-2 bg-forest-600 hover:bg-forest-700 disabled:opacity-50 text-white px-6 py-3 rounded-xl font-medium transition-colors"
        >
          <Sparkles size={16} />
          Get Recommendations
        </button>
      </div>

      {error && <div className="bg-red-50 text-red-600 rounded-xl p-4 mb-6">{error}</div>}
      {loading && <GridSkeleton count={9} />}
      {!loading && results.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {results.map((r) => <RecipeCard key={r.id} recipe={r} />)}
        </div>
      )}
      {!loading && recommended && results.length === 0 && !error && (
        <div className="text-center py-20 text-stone-400">No recipes found for those ingredients.</div>
      )}
    </div>
  );
}
