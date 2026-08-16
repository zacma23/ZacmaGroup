import 'dart:convert';

import 'package:http/http.dart' as http;

class ApiClient {
  ApiClient(this.token);

  final String baseUrl = 'http://localhost:8000/api/v1';
  final String token;

  Future<dynamic> chatWithAgent(String agentName, String message) async {
    final response = await http.post(
      Uri.parse('$baseUrl/ai/chat/$agentName'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({"message": message}),
    );

    return jsonDecode(response.body);
  }
}
