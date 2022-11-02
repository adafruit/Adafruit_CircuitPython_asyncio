"""
example that reads from the cdc data serial port in groups of four and prints
to the console. The USB CDC data serial port will need enabling. This can be done
by copying examples/usb_cdc_boot.py to boot.py in the CIRCUITPY directory

Meanwhile a simple counter counts up every second and also prints
to the console.
"""


import asyncio
import usb_cdc

async def client():
    usb_cdc.data.timeout=0
    s = asyncio.StreamReader(usb_cdc.data)
    while True:
        text = await s.readline()
        print(text)
        await asyncio.sleep(0)

async def counter():
    i = 0
    while True:
        print(i)
        i += 1
        await asyncio.sleep(1)

async def main():
    client_task = asyncio.create_task(client())
    count_task = asyncio.create_task(counter())
    await asyncio.gather(client_task, count_task)

asyncio.run(main())
