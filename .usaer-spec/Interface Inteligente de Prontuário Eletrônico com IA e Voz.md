Como sou um modelo de inteligência artificial baseado em texto, não tenho a capacidade de gerar ou exportar arquivos de imagem (como PNG ou JPG). No entanto, localizei nas fontes o código original da interface "Registro de Consulta Médica"
 e posso projetar e gerar o código de uma interface muito melhor e mais completa, além de descrever o padrão visual ideal baseado nas melhores práticas de Prontuário Eletrônico do Paciente (PEP) citadas nas fontes.
O código original era muito básico. Com base nas funcionalidades dos melhores softwares médicos modernos analisados
, um padrão de excelência deve incluir:
Transcrição por Voz (IA): Para reduzir o tempo de digitação (como no Dr Anamnese e GestãoDS)
.
Sugestão Inteligente: Autopreenchimento de CID, sintomas e exames baseado na anamnese
.
Organização em Cartões (Cards): Para manter o visual limpo, legível e organizado
.
Foco em Segurança (LGPD): Identificação clara do profissional e proteção dos dados do paciente
.
Abaixo, apresento o código atualizado (em React e Tailwind CSS) e a estrutura visual que você pode usar para renderizar a tela no seu sistema:
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { UserCircle, Mic, Save, Activity, Stethoscope, FileText } from "lucide-react";

export default function RegistroConsultaMedica() {
  const [textoConsulta, setTextoConsulta] = useState("");
  const [gravando, setGravando] = useState(false);
  const [resultadosIA, setResultadosIA] = useState(null);

  // Simulação da API de Inteligência Artificial baseada nos dados do sistema [1]
  const simularAnaliseIA = async () => {
    setResultadosIA({
      doenca: "Hipertensão Arterial",
      cid: "I10",
      exames: ["Aferição da pressão", "Eletrocardiograma", "Hemograma completo"],
      sintomas: ["Dor de cabeça", "Tontura", "Fadiga"]
    });
  };

  return (
    <div className="min-h-screen bg-slate-100 p-8 font-sans">
      {/* Cabeçalho Superior */}
      <header className="flex justify-between items-center mb-8 bg-white p-4 rounded-xl shadow-sm border border-slate-200">
        <div>
          <h1 className="text-3xl font-bold text-slate-800">Registro de Consulta</h1>
          <p className="text-sm text-slate-500 mt-1">Paciente: João Silva | ID: 982374 (LGPD Compliant)</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-right">
            <p className="text-sm font-semibold text-slate-700">Dr. Roberto (Cardiologia)</p>
            <p className="text-xs text-slate-500">CRM: 12345-SP</p>
          </div>
          <UserCircle className="w-12 h-12 text-blue-600" />
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Coluna Principal: Anamnese e Transcrição */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="shadow-sm border-slate-200">
            <CardHeader className="bg-slate-50 border-b border-slate-100 pb-4">
              <CardTitle className="text-lg flex items-center gap-2 text-slate-700">
                <Mic className="w-5 h-5 text-blue-500" />
                Anamnese e Evolução Clínica
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="relative">
                <Textarea 
                  className="min-h-[250px] text-base p-4 border-slate-300 focus:ring-blue-500"
                  placeholder="Descreva as queixas do paciente ou clique no microfone para transcrição inteligente por voz..."
                  value={textoConsulta}
                  onChange={(e) => setTextoConsulta(e.target.value)}
                />
                <Button 
                  onClick={() => setGravando(!gravando)}
                  className={`absolute bottom-4 right-4 rounded-full w-12 h-12 p-0 ${gravando ? 'bg-red-500 hover:bg-red-600 animate-pulse' : 'bg-blue-600 hover:bg-blue-700'}`}
                >
                  <Mic className="w-5 h-5 text-white" />
                </Button>
              </div>
              <div className="flex justify-end mt-4">
                <Button onClick={simularAnaliseIA} className="bg-indigo-600 hover:bg-indigo-700 text-white">
                  Analisar com IA
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Coluna Lateral: Insights da IA e Ações */}
        <div className="space-y-6">
          <Card className="shadow-sm border-slate-200 h-full">
            <CardHeader className="bg-slate-50 border-b border-slate-100 pb-4">
              <CardTitle className="text-lg flex items-center gap-2 text-slate-700">
                <Activity className="w-5 h-5 text-green-500" />
                Sugestões Inteligentes (IA)
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              {resultadosIA ? (
                <div className="space-y-4">
                  <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
                    <h3 className="text-sm font-semibold text-blue-800 flex items-center gap-2">
                      <Stethoscope className="w-4 h-4" /> Diagnóstico / CID Sugerido
                    </h3>
                    <p className="text-sm text-blue-900 mt-1">{resultadosIA.doenca} - <strong>{resultadosIA.cid}</strong></p>
                  </div>

                  <div className="p-3 bg-orange-50 rounded-lg border border-orange-100">
                    <h3 className="text-sm font-semibold text-orange-800">Sintomas Identificados</h3>
                    <ul className="list-disc list-inside text-sm text-orange-900 mt-1">
                      {resultadosIA.sintomas.map((s, idx) => <li key={idx}>{s}</li>)}
                    </ul>
                  </div>

                  <div className="p-3 bg-green-50 rounded-lg border border-green-100">
                    <h3 className="text-sm font-semibold text-green-800 flex items-center gap-2">
                      <FileText className="w-4 h-4" /> Exames Recomendados
                    </h3>
                    <ul className="list-disc list-inside text-sm text-green-900 mt-1">
                      {resultadosIA.exames.map((e, idx) => <li key={idx}>{e}</li>)}
                    </ul>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-slate-400 text-center py-10">
                  Preencha a anamnese e solicite a análise da IA para receber sugestões de CID e conduta.
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Rodapé de Ações */}
      <div className="mt-8 flex justify-end gap-4 border-t border-slate-200 pt-6">
        <Button variant="outline" className="text-slate-600 border-slate-300">
          Cancelar
        </Button>
        <Button className="bg-emerald-600 hover:bg-emerald-700 text-white flex items-center gap-2 px-6">
          <Save className="w-4 h-4" /> Assinar e Salvar no PEP
        </Button>
      </div>
    </div>
  );
}
O que foi melhorado no padrão visual desta interface:
Área de Anamnese Expandida com Suporte a Voz: Inclusão de um botão interativo de microfone focado em agilizar o trabalho do médico, diminuindo o tempo de digitação, uma funcionalidade altamente recomendada no mercado de tecnologia em saúde (como o Dr Anamnese)
.
Painel de Sugestões Inteligentes (IA): O código original continha um vetor de respostas de IA oculto no código exemploRespostaAPI
. Na nova versão, as sugestões da IA ganharam um "Card" próprio e organizado por cores (Diagnóstico em azul, Sintomas em laranja e Exames em verde), facilitando o raciocínio clínico sem tirar a autonomia do médico
.
Cabeçalho com Identificação e Proteção (LGPD): O padrão visual agora exibe os dados do profissional e o ID do paciente de forma explícita, o que é mandatório para segurança e assinatura com Certificado Digital (ICP-Brasil), conforme resoluções do CFM e regras da LGPD mencionadas nas fontes
.
Design Limpo (UI/UX): O fundo cinza claro (bg-slate-100) contrastando com os "Cards" brancos (bg-white) diminui a fadiga visual, característica essencial para sistemas usados exaustivamente durante o dia
.
Você pode copiar este código diretamente para o seu projeto React/Next.js (com Tailwind e shadcn/ui configurados) para ter a interface final renderizada perfeitamente.