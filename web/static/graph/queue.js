export class queue{
    constructor(){
        this.items = []
        this.length = 0;
    }

    enqueue(element){
        this.items.push(element);
        this.length+=1;
    }
    dequeue(){
        if(this.isEmpty()){
            console.warn("Underflow");
            return null;
        }
        this.length -= 1;
        this.items.shift();
    }
    peek(){
        if(this.isEmpty()){
            console.warn("Empty Queue");
            return null;
        }
        return this.items[0]
    }
    get(index){
        if(this.length <= index){
            console.warn("Index out of range");
        }
        return this.items[index]
    }
    isEmpty(){
        return this.items.length === 0;
    }
    toString(){
        return String(this.items)
    }

}