const http = require('http');
const fs = require('fs');
const path = require('path');
const maxApi = require("max-api");

const hostname = 'localhost';
const port = 8000;

fs.readFile('./index.html', function (err, html) {

    if (err) throw err;    

    http.createServer(function(request, response) {  
        response.writeHeader(200, {"Content-Type": "text/html"});  
        response.write(html);  
        response.end();  
    }).listen(port);
});


// const server = http.createServer((req, res) => {

//     res.writeHead(200, {
//         "Content-type": "text/html"
//       });
    
//     res.write("/index.html");
//     // console.log('Request for ' + req.url + ' by method ' + req.method);

//     // if (req.method == 'GET') {
//     //     var fileUrl;
//     //     if (req.url == '/') fileUrl = '/index.html';
//     //     else fileUrl = req.url;

//     //     var filePath = path.resolve('./public' + fileUrl);
//     //     const fileExt = path.extname(filePath);
//     //     if (fileExt == '.html') {
//     //         fs.exists(filePath, (exists) => {
//     //             if (!exists) {
//     //                 filePath = path.resolve('./public/404.html');
//     //                 res.statusCode = 404;
//     //                 res.setHeader('Content-Type', 'text/html');
//     //                 fs.createReadStream(filePath).pipe(res);
//     //                 return;
//     //             }
//     //             res.statusCode = 200;
//     //             res.setHeader('Content-Type', 'text/html');
//     //             fs.createReadStream(filePath).pipe(res);
//     //         });
//     //     }
//     //     else if (fileExt == '.css') {
//     //         res.statusCode = 200;
//     //         res.setHeader('Content-Type', 'text/css');
//     //         fs.createReadStream(filePath).pipe(res);
//     //     }
//     //     else {
//     //         filePath = path.resolve('./public/404.html');
//     //         res.statusCode = 404;
//     //         res.setHeader('Content-Type', 'text/html');
//     //         fs.createReadStream(filePath).pipe(res);
//     //     }
//     // }
//     // else {
//     //     filePath = path.resolve('./public/404.html');
//     //     res.statusCode = 404;
//     //     res.setHeader('Content-Type', 'text/html');
//     //     fs.createReadStream(filePath).pipe(res);
//     // }
// }).listen(8000, "127.0.0.1");


// // server.listen(port, hostname, () => {
// //     console.log(`Server running at http://${hostname}:${port}/`);
// // });