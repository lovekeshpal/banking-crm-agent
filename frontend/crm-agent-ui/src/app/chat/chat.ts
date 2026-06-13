import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../services/chat';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.html',
  styleUrl: './chat.css'
})
export class ChatComponent {
  messages: Message[] = [];
  userInput: string = '';
  isLoading: boolean = false;
  sessionId: string | undefined = undefined;

  constructor(private chatService: ChatService) {
    this.messages.push({
      role: 'assistant',
      content: '👋 Hello! I am your Banking CRM Assistant.\n\nI can help you:\n• Find high-value customers for loan outreach\n• Score customers by conversion likelihood\n• Generate personalized WhatsApp messages\n\nTry asking: "Find high-value customers likely to convert for a personal loan this month"',
      timestamp: new Date()
    });
  }

  sendMessage() {
    const message = this.userInput.trim();
    if (!message || this.isLoading) return;

    this.messages.push({
      role: 'user',
      content: message,
      timestamp: new Date()
    });

    this.userInput = '';
    this.isLoading = true;

    this.chatService.sendMessage(message, this.sessionId).subscribe({
      next: (response) => {
        this.sessionId = response.session_id;
        this.messages.push({
          role: 'assistant',
          content: response.response,
          timestamp: new Date()
        });
        this.isLoading = false;
        this.scrollToBottom();
      },
      error: () => {
        this.messages.push({
          role: 'assistant',
          content: '❌ Something went wrong. Please make sure the backend is running on port 8000.',
          timestamp: new Date()
        });
        this.isLoading = false;
      }
    });
  }

  onKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  scrollToBottom() {
    setTimeout(() => {
      const container = document.querySelector('.messages-container');
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    }, 100);
  }

  clearChat() {
    this.sessionId = undefined;
    this.messages = [{
      role: 'assistant',
      content: '👋 Chat cleared. How can I help you?',
      timestamp: new Date()
    }];
  }
}