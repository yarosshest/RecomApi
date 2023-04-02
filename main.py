import asyncio

async def my_coroutine(semaphore, i):
    async with semaphore:
        print(i)

async def main():
    # Create a semaphore with a limit of 5 coroutines
    semaphore = asyncio.Semaphore(100)

    # Create a list of coroutines
    coroutines = [my_coroutine(semaphore, i) for i in range(10000)]

    # Run the coroutines concurrently, limiting to 5 at a time
    await asyncio.gather(*coroutines)

# Run the main coroutine
asyncio.run(main())