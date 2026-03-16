export function CardSkeleton() {
  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm border border-stone-100 animate-pulse">
      <div className="h-4 bg-stone-200 rounded w-3/4 mb-3" />
      <div className="h-3 bg-stone-100 rounded w-full mb-2" />
      <div className="h-3 bg-stone-100 rounded w-5/6 mb-4" />
      <div className="flex gap-2">
        <div className="h-6 w-16 bg-stone-100 rounded-full" />
        <div className="h-6 w-16 bg-stone-100 rounded-full" />
      </div>
    </div>
  );
}

export function GridSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  );
}
