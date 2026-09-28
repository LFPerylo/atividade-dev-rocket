import { Spinner } from '@/shared/ui/Spinner'

export function PageLoading() {
  return (
    <div className="grid min-h-dvh place-items-center text-ink-400">
      <Spinner />
    </div>
  )
}
