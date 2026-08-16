import 'package:flutter/material.dart';

import 'core/api_client.dart';

void main() {
  runApp(const ZACMAMobileApp());
}

class ZACMAMobileApp extends StatelessWidget {
  const ZACMAMobileApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ZACMA Group',
      theme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo)),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    final client = ApiClient('demo-token');
    return Scaffold(
      appBar: AppBar(title: const Text('ZACMA Group AI')),
      body: Center(
        child: FutureBuilder(
          future: client.chatWithAgent('visa', 'Say hello in one word'),
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const CircularProgressIndicator();
            }
            if (snapshot.hasError) {
              return Text('Error: ${snapshot.error}');
            }
            final response = snapshot.data ?? {'response': 'ready'};
            return Text(response['response'] ?? 'ready');
          },
        ),
      ),
    );
  }
}
