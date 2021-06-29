
let mock = false;

export const callAPIGetAsync=(url, callback)=>{
    if(!mock){
        fetch(url)
        .then(res => res.json())
        .then((data) => {
            console.log(JSON.stringify(data))
            callback(data, false);
        })
        .catch((error)=>{
            callback(error, true);
        })
    }

}



export async function callAPIPost(url = '', data = {}, pathParm='') {
    if(!mock){
         // Default options are marked with *
        const response = await fetch(url+pathParm, {
            method: 'POST', // *GET, POST, PUT, DELETE, etc.
            mode: 'cors', // no-cors, *cors, same-origin
            cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
            credentials: 'same-origin', // include, *same-origin, omit
            headers: {
            'Content-Type': 'application/json'
            },
            redirect: 'follow', // manual, *follow, error
            referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
            body: JSON.stringify(data) // body data type must match "Content-Type" header
        });
        return response.json(); // parses JSON response into native JavaScript objects

    }
   
  }



export async function callAPIGet(url = '', queryParams = {}, pathParm='') {
    if(!mock){
         // Default options are marked with *
        const response = await fetch(url+pathParm, {
            method: 'GET', // *GET, POST, PUT, DELETE, etc.
            mode: 'cors', // no-cors, *cors, same-origin
            cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
            credentials: 'same-origin', // include, *same-origin, omit
            headers: {
            'Content-Type': 'application/json'
            },
            redirect: 'follow', // manual, *follow, error
            referrerPolicy: 'no-referrer' // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
           
        });
        return response.json(); // parses JSON response into native JavaScript objects

    }
   
  }