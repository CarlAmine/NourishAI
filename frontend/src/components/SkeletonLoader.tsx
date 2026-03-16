export function SkeletonLoader() {
  return (
    <div className="card p-6 space-y-4 animate-pulse">
      <div className="h-6 bg-cream-200 rounded-lg w-3/4"></div>
      <div className="space-y-3">
        <div className="h-4 bg-cream-200 rounded-lg w-full"></div>
        <div className="h-4 bg-cream-200 rounded-lg w-5/6"></div>
        <div className="h-4 bg-cream-200 rounded-lg w-4/6"></div>
      </div>
      <div className="flex gap-2 pt-2">
        <div className="h-8 bg-cream-200 rounded-full w-20"></div>
        <div className="h-8 bg-cream-200 rounded-full w-20"></div>
      </div>
    </div>
  )
}

export function SkeletonGrid({ count = 3 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonLoader key={i} />
      ))}
    </div>
  )
}
