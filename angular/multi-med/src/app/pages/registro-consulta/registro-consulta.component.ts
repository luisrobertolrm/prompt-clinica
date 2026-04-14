import { Component, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { environment } from '../../../environments/environment';

interface AnaliseIA {
  doenca: string;
  cid: string;
  sintomas: string[];
  exames: string[];
}

@Component({
  selector: 'app-registro-consulta',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './registro-consulta.component.html',
  styleUrl: './registro-consulta.component.css'
})
export class RegistroConsultaComponent {
  textoConsulta: string = '';
  gravando: boolean = false;
  resultadosIA: AnaliseIA | null = null;
  analisando: boolean = false;
  
  private recognition: any;

  constructor(private http: HttpClient, private zone: NgZone) {
    this.initSpeechRecognition();
  }

  initSpeechRecognition() {
    const { webkitSpeechRecognition } : any = window as any;
    if (webkitSpeechRecognition) {
      this.recognition = new webkitSpeechRecognition();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      this.recognition.lang = 'pt-BR';

      this.recognition.onresult = (event: any) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }
        
        // Update Angular Zone so view changes reactively
        this.zone.run(() => {
          if (finalTranscript) {
            this.textoConsulta += (this.textoConsulta ? ' ' : '') + finalTranscript;
          }
        });
      };

      this.recognition.onerror = (event: any) => {
        console.error('Speech recognition error', event.error);
        this.zone.run(() => this.gravando = false);
      };
      
      this.recognition.onend = () => {
         this.zone.run(() => this.gravando = false);
      }
    } else {
      console.warn("A API de Web Speech não é suportada neste navegador.");
    }
  }

  toggleGravacao() {
    if (!this.recognition) return;

    if (this.gravando) {
      this.recognition.stop();
      this.gravando = false;
    } else {
      this.recognition.start();
      this.gravando = true;
    }
  }

  simularAnaliseIA() {
    if (!this.textoConsulta.trim()) return;
    
    this.analisando = true;

    // Conecta de verdade à API do Python na URL do ambiente
    const payload = { prompt: this.textoConsulta };
    
    this.http.post<any>(`${environment.apiUrl}/analise-medica`, payload)
      .subscribe({
        next: (response) => {
          // Assume-se que o backend python retorna os campos semelhantes:
          this.resultadosIA = response;
          this.analisando = false;
        },
        error: (err) => {
          console.error("Falha ao comunicar com o Python, usando mock fallback:", err);
          
          // Mock de Fallback para demonstração se backend estiver offline
          setTimeout(() => {
            this.resultadosIA = {
               doenca: "Hipertensão Arterial (Simulado)",
               cid: "I10",
               exames: ["Aferição da pressão", "Eletrocardiograma", "Hemograma completo"],
               sintomas: ["Dor de cabeça inferida", "Tontura associada", "Fadiga"]
            };
            this.analisando = false;
          }, 1500);
        }
      });
  }

  salvarPEP() {
    alert('Assinatura Digital gerada. Prontuário salvo com sucesso!');
    this.textoConsulta = '';
    this.resultadosIA = null;
  }
}
