import { useState } from 'react';
import { Search } from 'lucide-react';
import { api } from '../lib/api';
import type { RecipeResult } from '../types/api';
import RecipeCard from '../components/RecipeCard';
import { GridSkeleton } from '../components/SkeletonLoader';

export default function RecipeSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<RecipeResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rerank, setRerank] = useState(true);
  const [topK, setTopK] = useState(9);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setSearched(true);
    try {
      const data = await api.searchRecipes({ query, top_k: topK, rerank });
      setResults(data.results);
    } catch {
      setError('Search failed. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold text-stone-800 mb-2">Recipe Search</h1>
      <p className="text-stone-500 mb-8">Semantic search powered by AI — describe what you're craving.</p>

      <div className="flex gap-3 mb-4">
        <div className="flex-1 relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-stone-400" size={18} />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="e.g. high protein pasta, vegan breakfast..."
            className="w-full pl-11 pr-4 py-3 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-forest-400 bg-white"
          />
        </div>
        <button
          onClick={handleSearch}
          disabled={loading}
          className="bg-forest-600 hover:bg-forest-700 disabled:opacity-50 text-white px-6 py-3 rounded-xl font-medium transition-colors"
        >
          Search
        </button>
      </div>

      <div className="flex items-center gap-4 mb-8 text-sm text-stone-600">
        <label className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" checked={rerank} onChange={(e) => setRerank(e.target.checked)} className="accent-forest-600" />
          Rerank results
        </label>
        <label className="flex items-center gap-2">
          Show
          <select
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            className="border border-stone-200 rounded-lg px-2 py-1 bg-white"
          >
            {[6, 9, 12, 18].map((n) => <option key={n}>{n}</option>)}
          </select>
          results
        </label>
      </div>

      {error && <div className="bg-red-50 text-red-600 rounded-xl p-4 mb-6">{error}</div>}
      {loading && <GridSkeleton count={topK} />}
      {!loading && results.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {results.map((r) => <RecipeCard key={r.id} recipe={r} />)}
        </div>
      )}
      {!loading && searched && results.length === 0 && !error && (
        <div className="text-center py-20 text-stone-400">
          No recipes found. Try a different query.
        </div>
      )}
    </div>
  );
}
