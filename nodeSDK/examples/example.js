import SantimpaySdk from "../lib/index.js";

// Santim Test
const PRIVATE_KEY_IN_PEM = `
-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIF1FiolOiNt9VZga7Xv2Hnc9ogec+n17oAC7vtls3fBuoAoGCCqGSM49
AwEHoUQDQgAEEcfE9DYOz/pkenjJ4Abdgr2BsYB5zhh+3RxlHA+ZDlQ63+RTJS2B
A2vqUeASic2BPMd+LqrAlo+5nCLqdBm//g==
-----END EC PRIVATE KEY-----
`

const GATEWAY_MERCHANT_ID = "9e2dab64-e2bb-4837-9b85-d855dd878d2b"

const client = new SantimpaySdk(GATEWAY_MERCHANT_ID, PRIVATE_KEY_IN_PEM);

// client side pages to redirect user to after payment is completed/failed
const successRedirectUrl = "https://santimpay.com";
const failureRedirectUrl = "https://santimpay.com";
const cancelRedirectUrl = "https://santimpay.com";

// backend url to receive a status update (webhook)
// const notifyUrl = "https://sant.requestcatcher.com/test";  
const notifyUrl = "https://webhook.site/783a4514-3e30-4315-9c68-c8b41a743c9d";

// custom ID used by merchant to identify the payment
const id = Math.floor(Math.random() * 1000000000).toString();
// console.log(id)

// client.generatePaymentUrl(id, 1, "payment", successRedirectUrl, failureRedirectUrl, notifyUrl, "+251913841405", cancelRedirectUrl).then(url => {
// // client.generatePaymentUrl(id, 1, "payment", successRedirectUrl, failureRedirectUrl, notifyUrl, "+251913841405", cancelRedirectUrl).then(url => {

//     // redirect user to url to process payment
//     console.log("Response Payment URL: ", url);
    
//     setTimeout(() => {

//         console.log("\n\n*********************************")
//         console.log("checking for transaction...")
        
//         client.checkTransactionStatus(id).then(transaction => {
//             console.log("Transaction status response: ", transaction);
//         }).catch(error => {
//             console.error(error)
//         })
//     }, 20_000)
// }).catch(error => {
//     console.error(error)
// })


client.directPayment(id, 1, "Payment for a coffee", notifyUrl, "+251913841405", "Telebirr").then(response => {
    console.log(response)
    client.checkTransactionStatus(id).then(transaction => {
        console.log("Transaction: ", transaction);
    }).catch(error => {
        console.error(error)
    })
}).catch(error => {
    console.error(error)
})



// client.sendToCustomer(id, 1, "refund for coffee", "+251984006406" , "Telebirr",notifyUrl).then(response => {
//     console.log(response)
// }).catch(error => {
//     console.error(error)
// })




// client.sendToCustomer(id, 1, "refund for coffee", "+251984006406" , "Telebirr", notifyUrl).then(response => {
//     console.log(response);
//     client.checkTransactionStatus(id).then(transaction => {
//         console.log("Transaction: ", transaction);
//     }).catch(error => {
//         console.error(error)
//     })
   
// }).catch(error => {
//     console.error(error)
// })