export interface NutritionInfo {
  calories: number | null;
  total_fat: number | null;
  total_sugar: number | null;
  sodium: number | null;
  protein: number | null;
  saturated_fat: number | null;
  carbs?: number | null;
}

export interface RecipeDetail {
  name: string;
  minutes: number | null;
  ingredients: string[];
  steps: string[];
  nutrition: NutritionInfo;
}

export interface ImagePredictResponse {
  predicted_class: string;
  recipe: RecipeDetail | null;
  error: string | null;
}

export interface RecipeSuggestion {
  match_score: number;
  recipe_text: string;
}

export interface SuggestResponse {
  results: RecipeSuggestion[];
}

export interface Recipe {
  id?: string;
  name: string;
  ingredients: string[];
  steps: string[];
  minutes?: number;
  tags?: string[];
  nutrition: NutritionInfo;
  match_score?: number;
}

export interface SearchRequest {
  query: string;
  top_k?: number;
  filters?: Record<string, unknown>;
  rerank?: boolean;
}

export interface SearchResponse {
  results: Recipe[];
}

export interface RecommendRequest {
  ingredients: string[];
  dietary_notes?: string;
  top_k?: number;
}

export interface RecommendResponse {
  results: Recipe[];
}

export interface MealPlan {
  date: string;
  meals: {
    breakfast?: Recipe;
    lunch?: Recipe;
    dinner?: Recipe;
  };
}

export interface MealPlanResponse {
  meal_plans: MealPlan[];
}

export interface NutritionData {
  date: string;
  total_calories: number;
  total_protein: number;
  total_carbs: number;
  total_fat: number;
  meals: Recipe[];
}

export interface NutritionResponse {
  data: NutritionData[];
}

export type AppMode = 'image' | 'ingredients';

export interface ApiError {
  detail: string;
}
