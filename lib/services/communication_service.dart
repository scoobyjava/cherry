import 'package:socket_io_client/socket_io_client.dart' as IO;

class CommunicationService {
  IO.Socket? _socket;

  // Replace with your server's address
  final String _serverUrl = 'http://localhost:3001';

  void connect(String userId) {
    _socket = IO.io(_serverUrl, <String, dynamic>{
      'transports': ['websocket'],
      'autoConnect': false,
    });

    _socket!.connect();

    _socket!.onConnect((_) {
      print('Connected to server');
      registerUser(userId);
    });

    _socket!.onDisconnect((_) => print('Disconnected from server'));
    _socket!.onConnectError((err) => print("Connect Error: $err"));
    _socket!.onError((err) => print("Error: $err"));

    // Listen for agent responses
    _socket!.on('agentResponse', (data) {
      print('Received agent response: $data');
      // Handle the agent's response (e.g., update the UI)
      // You'll likely want to use a Stream or Provider to manage this data
    });

      _socket!.on('agentResponseError', (data) {
          print('Received agent response error: $data');
          // Handle errors
      });
  }

  void registerUser(String userId) {
    if (_socket != null && _socket!.connected) {
      _socket!.emit('registerUser', userId);
    } else {
      print('Socket not connected. Cannot register user.');
    }
  }

  void sendMessageToAgent(String agentId, String message) {
    if (_socket != null && _socket!.connected) {
      _socket!.emit('sendMessageToAgent', {
        'userId': 'user123', // Replace with the actual user ID
        'agentId': agentId,
        'message': message,
      });
    } else {
      print('Socket not connected. Cannot send message.');
    }
  }

  void disconnect() {
    if (_socket != null) {
      _socket!.disconnect();
      _socket = null;
    }
  }
}
