**ML REST API**
===

neural-art (slow)
----------

* **URL**

  `/neural-art`

* **Method:**

  `POST`
  
* **Data Params**
 
   `content=[url-of-the-content-image]`

   `style=[url-of-the-style-image]`

   `num_iterations=[num-of-forward-passes]`

   `max-size=[max-image-size]`

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{ result_url : <todo..> }`
 
* **Error Response:**

  * **Code:** 400 BAD_REQUEST <br />
    **Content:** `{ "error" }`

* **Sample Call:**

    `curl -d "content=http://s3.amazonaws.com/factmag-images/wp-content/uploads/2017/02/cefa0d0aa7cd199d3a4b6202f7f300db.jpg&style=https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg&num_iterations=1000&maxsize=700" http://127.0.0.1:8080/neural-art`

  
fast-style-transfer (guess what)
----------

* **URL**

  `/fast-style-transfer`

* **Method:**

  `POST`
  
* **Data Params**
 
   `content=[url-of-the-content-image]`

   `checkpoint=[la_muse|rain_princess|scream|udnie|wave|wreck]`

   `max-size=[max-image-size]`

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{ result_url : <todo..> }`
 
* **Error Response:**

  * **Code:** 400 BAD_REQUEST <br />
    **Content:** `{ "error" }`

* **Sample Call:**

    `curl -d "content=https://scstylecaster.files.wordpress.com/2016/05/hot-surfer-guys-feat.jpg&checkpoint=scream.ckpt&maxsize=600" http://127.0.0.1:8080/fast-style-transfer`

  
