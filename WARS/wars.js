var MongoClient = require('mongodb').MongoClient;
var DATABASE_URL = "mongodb://localhost:27017/";

var util = require('util');
var bleno = require('./node_modules/bleno/index');
//var BatteryService = require('./examples/battery-service/battery-service.js');
var PythonShell = require('python-shell');
var pyShell = new PythonShell('DQN_Agent.py', { mode: 'json' });
var raspi = require('raspi-io');ㅎㅎㅎ
var five = require('johnny-five');
var board = new five.Board({ io: new raspi() });
var Sound = require('aplay');
var raspVol = require('raspberry-vol');

//var shell = new PythonShell('script.py', { mode: 'json '});
var that = this;
that._value = new Buffer(0);
that._updateValueCallback = null;
that.volumeValue = String();
that.dataFromDB = Array();
that.itisdone = false;

raspVol.get(function(err, level) {
    console.log('Current volume level is ' + level + '%');
    that.volumeValue = level.toString();
});

pyShell.on('message', function(message) {
    console.log(message);
    if (message.iamdone != undefined) {
        console.log("Loading Done");
        var jsonObj = { 'welldone': 1 };
        that.itisdone = true;
        pyShell.send(jsonObj);
    }
    if (message.action != undefined) {
        console.log(message.action);
        MongoClient.connect(DATABASE_URL, function(err, db) {
            if (err) throw err;
            var dbo = db.db("wars");
            dbo.collection('log').insertOne({
                "action": message.action,
                "date": new Date()
            }, function(err, result) {
                if (err) throw err;
                console.log("1 document inserted");
                db.close();
            });
        });
        var music = new Sound();
        switch (message.action) {
            case 1:
                music.play('wav/0001.wav');
                setTimeout(function() {
                    music.stop(); // stop the music after five seconds
                }, 5000);
                break;
            case 2:
                music.play('wav/0002.wav');
                setTimeout(function() {
                    music.stop(); // stop the music after five seconds
                }, 5000);
                break;
            case 3:
                music.play('wav/0003.wav');
                setTimeout(function() {
                    music.stop(); // stop the music after five seconds
                }, 5000);
                break;
            case 4:
                music.play('wav/0004.wav');
                setTimeout(function() {
                    music.stop(); // stop the music after five seconds
                }, 5000);
        }
    }
});

var BlenoPrimaryService = bleno.PrimaryService;
var BlenoCharacteristic = bleno.Characteristic;
var BlenoDescriptor = bleno.Descriptor;

console.log("bleno");

board.on('ready', function() {
    console.log('board is ready');
    var motion = new five.Motion('P1-36'); //a PIR is wired on pin 36 (GPIO 16)

    // 'calibrated' occurs once at the beginning of a session
    motion.on('calibrated', () => {
        console.log('calibrated');
        console.log('Loading...');
    });

    // "Motion detected" events
    motion.on('motionstart', () => {
        console.log('motionstart');
        if (that.itisdone) {
            var jsonObj = { 'detected': 1 };
            pyShell.send(jsonObj);
        }
        var detected = new Buffer('Motion Start!');
        console.log(detected);
        if (that._updateValueCallback) {
            console.log('NotifyOnlyCharacteristic update value: ' + detected);
            that._updateValueCallback(detected);
        }
    });

    // 'motionend' events
    motion.on('motionend', () => {
        console.log('motionend');
        //var jsonObj = { 'detected': 0 };
        //pyShell.send(JSON.stringify(jsonObj));
        var detected = new Buffer('Motion End!');
        if (that._updateValueCallback) {
            console.log('NotifyOnlyCharacteristic update value: ' + detected);
            that._updateValueCallback(detected);
        }
    });
});

// 이까지 모션 센서 제어 하는 부분 임
var StaticReadOnlyCharacteristic = function() {
    StaticReadOnlyCharacteristic.super_.call(this, {
        uuid: 'fffffffffffffffffffffffffffffff1',
        properties: ['read', 'write', 'writeWithoutResponse'],
        //value: that.volumeValue,
        descriptors: [
            new BlenoDescriptor({
                uuid: '2901',
                value: 'user description'
            })
        ]
    });
};
util.inherits(StaticReadOnlyCharacteristic, BlenoCharacteristic);

StaticReadOnlyCharacteristic.prototype.onReadRequest = function(offset, callback) {
    var result = this.RESULT_SUCCESS;
    var data = new Buffer(that.volumeValue);
    console.log('StaticReadAndWriteCharacteristic read request: ' + data.toString('hex') + ' ' + offset);
    if (offset > data.length) {
        result = this.RESULT_INVALID_OFFSET;
        data = null;
    } else {
        data = data.slice(offset);
    }

    callback(result, data);
};

StaticReadOnlyCharacteristic.prototype.onWriteRequest = function(data, offset, withoutResponse, callback) {
    console.log('StaticReadAndWriteCharacteristic write request: ' + data.toString() + ' ' + offset + ' ' + withoutResponse);
    raspVol.set(parseInt(data), function(err) {
        console.log('Changed volume to ' + data + '%');
    });
    that.volumeValue = data.toString();
    callback(this.RESULT_SUCCESS);
};

var DynamicReadOnlyCharacteristic = function() {
    DynamicReadOnlyCharacteristic.super_.call(this, {
        uuid: 'fffffffffffffffffffffffffffffff2',
        properties: ['read']
    });
};

util.inherits(DynamicReadOnlyCharacteristic, BlenoCharacteristic);

DynamicReadOnlyCharacteristic.prototype.onReadRequest = function(offset, callback) {
    var result = this.RESULT_SUCCESS;
    var data = new Buffer('dynamic value');

    if (offset > data.length) {
        result = this.RESULT_INVALID_OFFSET;
        data = null;
    } else {
        data = data.slice(offset);
    }

    callback(result, data);
};

// var LongDynamicReadOnlyCharacteristic = function() {
//   LongDynamicReadOnlyCharacteristic.super_.call(this, {
//     uuid: 'fffffffffffffffffffffffffffffff3',
//     properties: ['read']
//   });
// };

// util.inherits(LongDynamicReadOnlyCharacteristic, BlenoCharacteristic);

// LongDynamicReadOnlyCharacteristic.prototype.onReadRequest = function(offset, callback) {
//   var result = this.RESULT_SUCCESS;
//   var data = new Buffer(512);

//   for (var i = 0; i < data.length; i++) {
//     data[i] = i % 256;
//   }

//   if (offset > data.length) {
//     result = this.RESULT_INVALID_OFFSET;
//     data = null;
//   } else {
//     data = data.slice(offset);
//   }

//   callback(result, data);
// };

var WriteOnlyCharacteristic = function() {
    WriteOnlyCharacteristic.super_.call(this, {
        uuid: 'fffffffffffffffffffffffffffffff4',
        properties: ['write', 'writeWithoutResponse']
    });
};

util.inherits(WriteOnlyCharacteristic, BlenoCharacteristic);

WriteOnlyCharacteristic.prototype.onWriteRequest = function(data, offset, withoutResponse, callback) {
    console.log('WriteOnlyCharacteristic write request: ' + data.toString('hex') + ' ' + offset + ' ' + withoutResponse);

    callback(this.RESULT_SUCCESS);
};

var NotifyOnlyCharacteristic = function() {
    NotifyOnlyCharacteristic.super_.call(this, {
        uuid: 'fffffffffffffffffffffffffffffff5',
        properties: ['notify']
    });
};

util.inherits(NotifyOnlyCharacteristic, BlenoCharacteristic);

NotifyOnlyCharacteristic.prototype.onSubscribe = function(maxValueSize, updateValueCallback) {
    console.log('NotifyOnlyCharacteristic subscribe');
    // //this.counter = 0;
    // this.changeInterval = setInterval(function() {
    //   var data = new Buffer("Bird Detected!");
    //   //data.writeUInt32LE(this.counter, 0);

    //   console.log('NotifyOnlyCharacteristic update value: ' + data);
    //   updateValueCallback(data);
    //   //this.counter++;
    // }.bind(this), 1000);
    that._updateValueCallback = updateValueCallback;
};

NotifyOnlyCharacteristic.prototype.onUnsubscribe = function() {
    console.log('NotifyOnlyCharacteristic unsubscribe');
    // if (this.changeInterval) {
    //   clearInterval(this.changeInterval);
    //   this.changeInterval = null;
    // }
    that._updateValueCallback = null;
};

NotifyOnlyCharacteristic.prototype.onNotify = function() {
    console.log('NotifyOnlyCharacteristic on notify');
};

var IndicateOnlyCharacteristic = function() {
    IndicateOnlyCharacteristic.super_.call(this, {
        uuid: 'fffffffffffffffffffffffffffffff6',
        properties: ['indicate']
    });
};

util.inherits(IndicateOnlyCharacteristic, BlenoCharacteristic);

IndicateOnlyCharacteristic.prototype.onSubscribe = function(maxValueSize, updateValueCallback) {
    console.log('IndicateOnlyCharacteristic subscribe');

    this.counter = 0;
    this.changeInterval = setInterval(function() {
        var data = new Buffer(4);
        data.writeUInt32LE(this.counter, 0);

        console.log('IndicateOnlyCharacteristic update value: ' + this.counter);
        updateValueCallback(data);
        this.counter++;
    }.bind(this), 1000);
};

IndicateOnlyCharacteristic.prototype.onUnsubscribe = function() {
    console.log('IndicateOnlyCharacteristic unsubscribe');

    if (this.changeInterval) {
        clearInterval(this.changeInterval);
        this.changeInterval = null;
    }
};

IndicateOnlyCharacteristic.prototype.onIndicate = function() {
    console.log('IndicateOnlyCharacteristic on indicate');
};

var DBWriteAndNotifyCharacteristic = function() {
    DBWriteAndNotifyCharacteristic.super_.call(this, {
        uuid: 'fffffffffffffffffffffffffffffff7',
        properties: ['write', 'notify']
    });
};

util.inherits(DBWriteAndNotifyCharacteristic, BlenoCharacteristic);

DBWriteAndNotifyCharacteristic.prototype.onSubscribe = function(maxValueSize, updateValueCallback) {
    console.log('DBWriteAndNotifyCharacteristic subscribe');

    MongoClient.connect(DATABASE_URL, function(err, db) {
        if (err) throw err;
        var dbo = db.db("wars");
        var query = {
            date: { "$gte": new Date(new Date().setDate(new Date().getDate() - 1)), "$lte": new Date() }
        };
        dbo.collection('log').find(query).toArray(function(err, result) {
            if (err) throw err;
            if (result.length == 0) {
                var data = new Buffer(JSON.stringify(result));
                console.log(JSON.stringify(result));
                updateValueCallback(data);
            }
            for (var i = 0; i < result.length; i++) {
                if (i == result.length - 1) {
                    result[i].sendStatus = 0;
                } else {
                    result[i].sendStatus = 1;
                }
                var data = new Buffer(JSON.stringify(result[i]));
                console.log(JSON.stringify(result[i]));
                updateValueCallback(data);
            }
            db.close();
        });
    });

    //   this.counter = 0;
    //   this.changeInterval = setInterval(function() {
    //     var data = new Buffer(4);
    //     data.writeUInt32LE(this.counter, 0);

    //     console.log('DBWriteAndNotifyCharacteristic update value: ' + this.counter);
    //     updateValueCallback(data);
    //     this.counter++;
    //   }.bind(this), 5000);
};

DBWriteAndNotifyCharacteristic.prototype.onUnsubscribe = function() {
    console.log('DBWriteAndNotifyCharacteristic unsubscribe');

    //   if (this.changeInterval) {
    //     clearInterval(this.changeInterval);
    //     this.changeInterval = null;
    //   }
};

DBWriteAndNotifyCharacteristic.prototype.onNotify = function() {
    console.log('DBWriteAndNotifyCharacteristic on notify');
};

function SampleService() {
    SampleService.super_.call(this, {
        uuid: 'fffffffffffffffffffffffffffffff0',
        characteristics: [
            new StaticReadOnlyCharacteristic(),
            new DynamicReadOnlyCharacteristic(),
            //new LongDynamicReadOnlyCharacteristic(),
            new WriteOnlyCharacteristic(),
            new NotifyOnlyCharacteristic(),
            new IndicateOnlyCharacteristic(),
            new DBWriteAndNotifyCharacteristic()
        ]
    });
}

util.inherits(SampleService, BlenoPrimaryService);

bleno.on('stateChange', function(state) {
    console.log('on -> stateChange: ' + state + ', address = ' + bleno.address);
    if (state === 'poweredOn') {
        bleno.startAdvertising('WARS Advertising', ['fffffffffffffffffffffffffffffff0']);
    } else {
        bleno.stopAdvertising();
    }
});

// Linux only events /////////////////
bleno.on('accept', function(clientAddress) {
    console.log('on -> accept, client: ' + clientAddress);

    bleno.updateRssi();
});

bleno.on('disconnect', function(clientAddress) {
    console.log('on -> disconnect, client: ' + clientAddress);
});

bleno.on('rssiUpdate', function(rssi) {
    console.log('on -> rssiUpdate: ' + rssi);
});
//////////////////////////////////////

bleno.on('mtuChange', function(mtu) {
    console.log('on -> mtuChange: ' + mtu);
});

bleno.on('advertisingStart', function(error) {
    console.log('on -> advertisingStart: ' + (error ? 'error ' + error : 'success'));

    if (!error) {
        bleno.setServices([
            new SampleService()
            //new BatteryService()
        ]);
    }
});

bleno.on('advertisingStop', function() {
    console.log('on -> advertisingStop');
});

bleno.on('servicesSet', function(error) {
    console.log('on -> servicesSet: ' + (error ? 'error ' + error : 'success'));
});

// pyShell.end(function (err) {
//     if (err){
//       throw err;
//     };
//     console.log('finished');
// });