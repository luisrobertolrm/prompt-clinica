import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { environment } from '../../../environments/environment';

interface Noticia {
  titulo: string;
  resumo: string;
  data: string;
}

interface ChatMessage {
  origem: 'ia' | 'user';
  texto: string;
}

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule, RouterModule, HttpClientModule, FormsModule],
  templateUrl: './landing.component.html',
  styleUrl: './landing.component.css'
})
export class LandingComponent implements OnInit {
  
  noticias: Noticia[] = [];
  
  // Chat Widget
  isChatOpen: boolean = false;
  chatInput: string = '';
  isTyping: boolean = false;
  chatMessages: ChatMessage[] = [
    { origem: 'ia', texto: 'Olá! Sou a assistente virtual da Multi Med. Como posso te ajudar hoje? (ex: "Quero marcar uma consulta")' }
  ];

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.carregarNoticias();
  }

  carregarNoticias() {
    this.http.get<Noticia[]>(`${environment.apiUrl}/noticias`).subscribe({
      next: (res) => {
         this.noticias = res.slice(0, 4);
      },
      error: () => {
         // Fallback se API backend off
         this.noticias = [
           { titulo: 'Nova Ala Cardiológica Inaugurada', resumo: 'A Multi Med orgulha-se de entregar novos equipamentos para diagnósticos do coração de última geração.', data: '12 Abr 2026' },
           { titulo: 'Campanha de Vacinação', resumo: 'Programe e atualize sua carteira de vacinação diretamente nas nossas dependências com agilidade.', data: '05 Abr 2026' },
           { titulo: 'Dicas de Bem Estar', resumo: 'Confira 5 hábitos essenciais que profissionais formados recomendam para manter a longevidade intacta.', data: '22 Mar 2026' }
         ];
      }
    });
  }

  toggleChat() {
    this.isChatOpen = !this.isChatOpen;
  }

  sendMessage() {
    const txt = this.chatInput.trim();
    if (!txt) return;

    this.chatMessages.push({ origem: 'user', texto: txt });
    this.chatInput = '';
    this.isTyping = true;

    // Simulação do backend de IA (LLM / LangGraph fallback simulado por tempo)
    setTimeout(() => {
       this.isTyping = false;
       const response = this.evaluateSimpleIntent(txt);
       this.chatMessages.push({ origem: 'ia', texto: response });
    }, 1500);
  }

  // Fallback engine puramente visual se a api local não bater IA.
  evaluateSimpleIntent(text: string): string {
    const low = text.toLowerCase();
    if(low.includes('marcar') || low.includes('agendar')) {
      return 'Entendido! Para marcar sua consulta com segurança e ver a agenda completa, clique no botão superior "Entrar no Sistema". Estarei te esperando lá!';
    }
    if(low.includes('cancelar') || low.includes('confirmar')) {
      return 'Para gerenciar seus agendamentos, será necessário realizar a autenticação. É rapidinho!';
    }
    return 'Sou uma Inteligência focada em atendimento. Aconselho você a Entrar no Sistema para que possamos trocar dados com segurança médica!';
  }
}
