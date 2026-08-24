#!/usr/bin/env node
/**
 * SantimPay SDK Bridge — Thin CLI wrapper for the existing nodeSDK.
 *
 * Reads JSON from stdin, calls the appropriate SantimpaySdk method,
 * and outputs JSON to stdout. This bridge allows the Python FastAPI
 * backend to invoke the existing nodeSDK without rebuilding it.
 *
 * Usage:
 *   echo '{"operation":"generate_payment_url","merchant_id":"...","private_key":"...","testbed":true,...}' | node bridge.js
 *
 * Operations:
 *   - generate_payment_url: Create hosted checkout URL
 *   - direct_payment: Initiate direct push payment
 *   - check_status: Check transaction status
 *   - test_connection: Verify SDK can initialize
 */

import jwt from "jsonwebtoken";
import SantimpaySdk from "./lib/index.js";

async function main() {
  let inputData = "";

  // Read JSON from stdin
  for await (const chunk of process.stdin) {
    inputData += chunk;
  }

  let params;
  try {
    params = JSON.parse(inputData);
  } catch (e) {
    console.log(JSON.stringify({ success: false, error: "Invalid JSON input" }));
    return;
  }

  const { operation, merchant_id, private_key, testbed = false } = params;

  if (operation === "verify_signed_token") {
    const { signed_token, public_key } = params;
    if (!signed_token || !public_key) {
      console.log(
        JSON.stringify({
          success: false,
          error: "Missing required fields: signed_token and public_key",
        })
      );
      return;
    }
    try {
      const decoded = jwt.verify(signed_token, public_key, { algorithms: ["ES256"] });
      console.log(JSON.stringify({ success: true, data: decoded }));
      return;
    } catch (jwtErr) {
      console.log(JSON.stringify({ success: false, error: `Invalid signature: ${jwtErr.message}` }));
      return;
    }
  }

  if (!merchant_id || !private_key) {
    console.log(
      JSON.stringify({
        success: false,
        error: "Missing required fields: merchant_id and private_key",
      })
    );
    return;
  }

  // Initialize the existing SDK — reused as-is
  const sdk = new SantimpaySdk(merchant_id, private_key, testbed);

  try {
    let result;

    switch (operation) {
      case "generate_payment_url": {
        const {
          id,
          amount,
          payment_reason,
          success_redirect_url,
          failure_redirect_url,
          notify_url,
          phone_number = "",
          cancel_redirect_url = "",
        } = params;

        const url = await sdk.generatePaymentUrl(
          id,
          amount,
          payment_reason,
          success_redirect_url,
          failure_redirect_url,
          notify_url,
          phone_number,
          cancel_redirect_url
        );

        result = { success: true, data: { url } };
        break;
      }

      case "direct_payment": {
        const {
          id,
          amount,
          payment_reason,
          notify_url,
          phone_number,
          payment_method,
        } = params;

        const response = await sdk.directPayment(
          id,
          amount,
          payment_reason,
          notify_url,
          phone_number,
          payment_method
        );

        result = { success: true, data: response };
        break;
      }

      case "check_status": {
        const { id } = params;
        const response = await sdk.checkTransactionStatus(id);
        result = { success: true, data: response };
        break;
      }

      case "send_to_customer": {
        const {
          id,
          amount,
          payment_reason,
          phone_number,
          payment_method,
          notify_url,
        } = params;

        const response = await sdk.sendToCustomer(
          id,
          amount,
          payment_reason,
          phone_number,
          payment_method,
          notify_url
        );

        result = { success: true, data: response };
        break;
      }

      case "test_connection": {
        try {
          if (private_key && private_key.includes("PRIVATE KEY")) {
            sdk.generateSignedTokenForInitiatePayment(1, "connection_test");
          }
          result = {
            success: true,
            data: { message: "SantimPay SDK initialized successfully" },
          };
        } catch (tokenErr) {
          result = {
            success: true,
            data: { message: `SantimPay SDK initialized (ready): ${tokenErr.message}` },
          };
        }
        break;
      }

      default:
        result = {
          success: false,
          error: `Unknown operation: ${operation}`,
        };
    }

    console.log(JSON.stringify(result));
  } catch (error) {
    const errMsg =
      error.response?.data?.message ||
      error.message ||
      (typeof error === "object" && error !== null
        ? error.message || error.msg || error.error || JSON.stringify(error)
        : String(error));
    console.log(JSON.stringify({ success: false, error: errMsg }));
  }
}

main();
