# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 Dan Halbert for Adafruit Industries
# SPDX-License-Identifier: Unlicense
# Contributor: Sean Carney

"""
Example that illustrates how to use asyncio to execute two functions at 
user-defined time intervals.  
"""

# Imports
import asyncio
from adafruit_ticks import ticks_ms, ticks_add, ticks_less, ticks_diff

async def function_1():
    print('Execturing function_1')
    await asyncio.sleep(0)
    
async def function_2(led):
    print('Execturing function_2')
    await asyncio.sleep(0)

async def main():

    # Desired time delays in milliseconds
    delay_1 = 1000
    delay_2 = 100
    
    # Set start of frame
    start_function_1 = ticks_ms()
    start_function_2 = ticks_ms()    
        
    while True:    
      
        if ticks_diff(ticks_ms(), start_function_1 ) > delay_1:
            start_function_1 = ticks_ms()
            asyncio.create_task(function_1())
            
        if ticks_diff(ticks_ms(), start_function_2) > delay_2:
            start_function_2 = ticks_ms()
            asyncio.create_task(function_2())
        
        await asyncio.sleep(0)
        
asyncio.run(main(led)) 
