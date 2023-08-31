var MongoClient = require('mongodb').MongoClient;
var DATABASE_URL = "mongodb://localhost:27017/";

// MongoClient.connect(DATABASE_URL, function(err, db) {
//   if (err) throw err;
//   var dbo = db.db("wars");
//   var myobj = { name: "Company Inc", address: "Highway 37" };
//   dbo.collection("customers").insertOne(myobj, function(err, res) {
//     if (err) throw err;
//     console.log("1 document inserted");
//     db.close();
//   });
// });
    var data = new Buffer(512);
    MongoClient.connect(DATABASE_URL, function(err, db) {
        if (err) throw err;
        console.log(new Date(new Date().setDate(new Date().getDate()-1)));
        var dbo = db.db("wars");
        var query = {
            date : { "$gte": new Date(new Date().setDate(new Date().getDate()-1)), "$lte": new Date() }
        };
        dbo.collection('log').find(query).toArray( function(err, result) {
            if (err) throw err;
            //data = result;
            for (var i = 0; i < result.length; i++) {
                this.data[i] = JSON.stringify(result[i]);
                console.log(JSON.stringify(result[i]));
            }
            console.log(data);
            db.close();
        });
    });