// src/utils/notificationService.ts
import { io } from '../api/agentRouter'; // Import the io instance

export function sendNotification(userId: string, message: string) {
  // Find the socket associated with the user ID
    for (let [id, socket] of io.sockets.sockets) {
        if (socket.data.userId === userId) {
            socket.emit('notification', { message });
            return;
        }
    }
}
