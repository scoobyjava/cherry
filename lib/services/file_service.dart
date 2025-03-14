import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'dart:io';

class FileService {
    final String _baseUrl = "http://localhost:3001"; // Your server address

    Future<String?> uploadFile(File file) async {
        var request = http.MultipartRequest('POST', Uri.parse('$_baseUrl/upload'));
        request.files.add(
            await http.MultipartFile.fromPath(
                'file',
                file.path,
                contentType: MediaType('application', 'octet-stream'), // Adjust as needed
            )
        );

        try {
            var streamedResponse = await request.send();
            var response = await http.Response.fromStream(streamedResponse);

            if (response.statusCode == 200) {
                print('File uploaded successfully');
                // Parse the response (assuming it's JSON)
                // You might return the filename or a URL to the uploaded file
                return response.body;
            } else {
                print('File upload failed: ${response.statusCode}');
                return null;
            }
        } catch (e) {
            print('Error uploading file: $e');
            return null;
        }
    }
}
