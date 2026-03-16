export interface RecipeFilters {
  dietary?: string[];
  cuisine?: string;
  max_time?: number;
  min_rating?: number;
}

export interface RecipeSearchRequest {
  query: string;
  top_k?: number;
  filters?: RecipeFilters;
  rerank?: boolean;
  include_diagnostics?: boolean;
  candidate_k?: number;
}

export interface RecommendRequest {
  ingredients: string[];
  dietary_notes?: string;
  top_k?: number;
  filters?: RecipeFilters;
  rerank?: boolean;
  include_diagnostics?: boolean;
  candidate_k?: number;
}

export interface RecipeResult {
  id: string;
  name: string;
  description?: string;
  ingredients: string[];
  instructions?: string[];
  nutrition?: NutritionInfo;
  cuisine?: string;
  dietary_tags?: string[];
  prep_time?: number;
  cook_time?: number;
  servings?: number;
  rating?: number;
  score?: number;
  image_url?: string;
}

export interface NutritionInfo {
  calories?: number;
  protein?: number;
  carbs?: number;
  fat?: number;
  fiber?: number;
  sugar?: number;
}

export interface RecipeSearchResponse {
  results: RecipeResult[];
  diagnostics?: Record<string, unknown>;
}

export interface MealSlot {
  recipe?: RecipeResult;
  meal_type: 'breakfast' | 'lunch' | 'dinner';
}

export interface DayPlan {
  day: string;
  meals: MealSlot[];
}

export interface MealPlanResponse {
  week: DayPlan[];
}

export interface NutritionDay {
  date: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
}

export interface NutritionResponse {
  days: NutritionDay[];
  averages: NutritionInfo;
}

export interface HealthResponse {
  status: string;
  version: string;
  models_loaded: boolean;
}
