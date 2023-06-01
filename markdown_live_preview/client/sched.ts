export const sched = (
  cycle: number,
): AsyncIterable<void> & { reset: () => void } => {
  let cb = (): void => undefined
  let timeout: Parameters<typeof clearTimeout>[0] = undefined

  return {
    async *[Symbol.asyncIterator]() {
      while (true) {
        await new Promise<void>((resolve) => {
          cb = resolve
          timeout = setTimeout(resolve, cycle)
        })
        yield
      }
    },
    reset() {
      clearTimeout(timeout)
      timeout = setTimeout(cb, cycle)
    },
  }
}
