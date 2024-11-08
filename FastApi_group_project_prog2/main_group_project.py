from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import uvicorn
from typing import List
from datetime import datetime

app = FastAPI() # Creating the FastAPI app  

class Classroom(BaseModel): #Creating a  response model for classrooms
    id: int
    name: str
    capacity: int

class Booking(BaseModel):# Creating a response model for bookings
    id: str
    classroom_id: int
    classroom_name: str
    start_time: datetime
    end_time: datetime

# Database of classrooms
classroom_db = {
    1: Classroom(id=1, name="A101", capacity=31),
    2: Classroom(id=2, name="A102", capacity=28),
    3: Classroom(id=3, name="A103", capacity=21)
}

# Database for bookings 
booking_db = []

def is_time_slot_available(classroom_id: int, requested_start_time: datetime, requested_end_time: datetime,) -> bool:
   
    """ 
        This function, is created to check if a time slot is occupied. We use a simple for loop to iterate over booking database, to check
        if the classroom is booked and then goes on to check the start and end times.  
    
        Args: 
            Arguments are taken from Booking class. 
            requested start time is created for this function.
            requested_End_time is created for this function. 
            
        Returns: 
            This function returns true, if the time slot is available 
        
        Raise: 
            httpexecption: raises 400 status code if start time is in the past
            httpexecption: raises 409 status code if the bookings overlap

    """
    current_time = datetime.now() # Fetching current time and date

    if requested_start_time < current_time: 
        raise HTTPException(status_code=400, detail="start time is in the past")
        
    for existing_booking in booking_db:
        if existing_booking.classroom_id == classroom_id: #Checks if classroom has existing booking
           if (requested_start_time < existing_booking.end_time and
                requested_end_time > existing_booking.start_time): #Checks if time slot is available for specific classroom 
                raise HTTPException(status_code=409, detail="This classroom is already booked at requested time")

    return True
    

@app.get("/classrooms/", response_model=List[Classroom]) 
def list_classrooms(): 
    return list(classroom_db.values()) #Returns all classrooms 


@app.post("/booking/{classroom_id}", response_model=Booking)
def book_classroom(classroom_id: int, start_time: datetime, end_time: datetime):
    """ 
    
    This function is created to book classrooms. With the help of is_time_slot_available it also
    handles error messages
        
    Args:
        Using Arguments following the response model Booking
             
    
    Write classroom_ID and time (example):

        classroom_ID, either 1,2 or 3 
        start time, 2024-11-07t13:30 
        end time, 2024-11-07t16:30
        

    Entire request path with querys example:
     
        /booking/3?start_time=2024-12-10t15%3A30&end_time=2024-12-11t17%3A30

    returns: 
        this function returns a booking if successfull 

    raise:

        httpexecption: raises 400 status code if start time is in the past
        httpexecption: raises 404 status code if the classroom does not exist
        httpexecption: raises 409 status code if the bookings overlap

    """
    
    classroom = classroom_db.get(classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found.")
    
    if not is_time_slot_available(classroom_id, start_time, end_time): 
        raise HTTPException(status_code=409, detail="This classroom is already booked at requested time")
    
    booking = Booking( # This variable is a copy of our booking model, but adds a unique booking ID 
        id=str(uuid.uuid4()),
        classroom_id=classroom.id,
        classroom_name=classroom.name,
        start_time=start_time,
        end_time=end_time
    )
    
    booking_db.append(booking)
    return booking


@app.delete("/booking/{booking_id}", response_model=Booking)
def delete_booking(booking_id: str):
    """
        Delete a booking by ID and return the deleted booking details.
    
        We used a simple for loop, to iterate over the booking database with the key b, then we 
        compare the key(b) and the booking database booking_ID, to see if they're the same.
        we also make sure to remove the booking from the booking database. 

        Entire path example:

            /booking/94f70b2e-72e7-4780-bb84-8fd577ffefaf 
            
        returns:
                this function returns the deleted booking, if DELETE successfull 
      
        raise:

            httpexecption: raises 404 status code if we can't find the booking. 
    """
      
    for b in booking_db: 
        if b.id == booking_id:
            booking = b
            booking_db.remove(booking)
            return booking      
    else:
        raise HTTPException(status_code=404, detail="Booking not found.")
    

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8030, reload=True)
