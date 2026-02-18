from fastapi import FastAPI,Depends,HTTPException
from schemas import Todo as TodoSchema,TodoCreate
from sqlalchemy.orm import Session
from database import SessionLocal,Base,engine
from models import Todo
Base.metadata.create_all(bind=engine)

app= FastAPI()

#dependency for db:session
def get_db():
    db=SessionLocal() # we can get db obj from here
    try:
        yield db
    finally:
        db.close()# the database session must be closed once after sending it to the route

#CREATE TODO
@app.post("/todos",response_model=TodoSchema)

def create(todo: TodoCreate,db: Session=Depends(get_db)): # main todo task code
    db_todo = Todo (**todo.dict())#-> converting into a dictionary ->** is for unpacking the values
    db.add(db_todo) # stores the values only in the memory not in the database
    db.commit() # actully stores in table
    db.refresh(db_todo)  # it will get the id from todo schema once stored from the table
    return db_todo

#GET TODO

@app.get("/todos" , response_model=list[TodoSchema])

def read_Todos(db: Session=Depends(get_db)):
    return db.query(Todo).all()

#GET SINGLE TODO
@app.get("/todos/{todo_id}", response_model=TodoSchema)

def read_Todo(todo_id : int,db: Session=Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code= 404, detail= "Todo not found")
    return todo


#PUT ROTE-UPDATE TODO
@app.put("/todos/{todo_id}", response_model=TodoSchema)
def update_todo( todo_id : int, updated: TodoCreate , db: Session=Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code= 404, detail= "Todo not found")
    for key,value in updated.dict().items(): 
        setattr(todo ,key,value)
    db.commit()
    db.refresh(todo)
    return todo

#DELETE TODO

@app.delete("/todos/{todo_id}") #--------> nothing to return so just path is enough

def delete_todo(todo_id : int,  db: Session=Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code= 404, detail= "Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted successfully"}
