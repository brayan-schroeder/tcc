using CityTrafficSimulator;
using System;
using System.Threading;
using System.Web.Http;
using System.Xml;

namespace WebApiStarter.Template1.Controllers
{
    public class TestController : ApiController
    {
        [HttpPost, Route("avaliar")]
        public IHttpActionResult Post([FromBody]dynamic value)
        {
            string cromossomo = value.cromossomo.ToString();
            int tempoExecucaoSimulador = Convert.ToInt32(value.tempoExecucaoSimulador);
            double totalTempoMedioViagem = 0;

            XmlDocument xml = new XmlDocument();

            xml.Load("C:\\Users\\Brayan Schroeder\\Documents\\TCC II\\Simulacoes\\JoinvilleTemplate.xml"); // Abre o XML de configuração

            XmlNodeList xmlNodeList = xml.GetElementsByTagName("events"); // Pega o nó de eventos que servirão para adicionar as configurações dos semáforos

            int posicao = 0; // Posição do vetor
            foreach (XmlNode no in xmlNodeList)
            {
                string semaforo = cromossomo.Substring(posicao * 6, 6); // Pega a configuração de tempo do semáforo em questão

                for (int o = 0; o <= 5; o++) // O cromossomo possui 6 caracteres, a posição define o intervalo e o valor (1/0) define se este ficará acionado neste intervalo
                {
                    bool ativo = semaforo[o].Equals('1');

                    if (ativo) // Se este estiver ativo, será configurado um acionamento de 10 segundos do semáforo para a posição em questão
                    {
                        int inicio = o * 10; // Intervalo de início do ativamento
                        int fim = inicio + 10; // Fim do intervalo de ativamento
                        const string tempoIntervalo = "10"; // Tempo de intervalo

                        using (XmlWriter writer = no.CreateNavigator().AppendChild()) // Manipula o nó
                        {
                            writer.WriteStartElement("TimelineEvent", ""); // Cria um novo elemento de configuração do semáforo
                            writer.WriteElementString("eventTime", "", inicio.ToString());
                            writer.WriteElementString("eventLength", "", tempoIntervalo);
                            writer.WriteElementString("eventEndTime", "", fim.ToString());
                            writer.WriteElementString("argbColor", "", "-16744448"); // Padrão do template de configuração do simulador
                            writer.WriteEndElement(); // Finaliza a criação do elemento
                        }
                    }
                }
                
                posicao++;
            }

            xml.Save("C:\\Users\\Brayan Schroeder\\Documents\\TCC II\\Simulacoes\\Joinville.xml"); // Salva o xml em um novo arquivo

            MainForm ctf = new MainForm();

            ctf.loadForm(); // Inicializa o simulador
            ctf.loadFile("C:\\Users\\Brayan Schroeder\\Documents\\TCC II\\Simulacoes\\Joinville.xml"); // Carrega o arquivo com as configurações de semáforo, volume de veículos, etc
            ctf.turnSimulationOn(); // Liga o simulador

            this.WaitNSeconds(tempoExecucaoSimulador); // Deixa o simulador executando pelo número de segundos parâmetrizados

            ctf.turnSimulationOff(); // Desliga o simulador

            foreach(var inicio in ctf.getTrafficVolumeForm().getListStartNodes().Items)
            {
                foreach(var destino in ctf.getTrafficVolumeForm().getListDestinationNodes().Items)
                {
                    totalTempoMedioViagem += ctf.getTrafficVolumeForm().getEstatistica(inicio, destino); // Pega o tempo médio de viagem em segundos para cada rota possível
                }
            }

            // Caso aconteça um overflow na aplicação e gere um tempo médio de viagem infinito, retorna um tempo de 3000 segundos, o que já invalida o resultado, vide que a média
            // para as execuções é por volta de ~ 1200 segundos numa simulação de 30 segundos (utilizada no trabalho em questão) e ~ 2100 numa simulação de 60 segundos
            if (Double.IsInfinity(totalTempoMedioViagem))
                totalTempoMedioViagem = 3000;

            // Caso aconteça do algoritmo genético simular um indivíduo com todos os semáforos fechados, fazendo com que a média de cada rota seja 1s (ou seja, nenhum veículo
            // chegou ao destino)
            if (totalTempoMedioViagem <= 100)
                totalTempoMedioViagem = 3000;

            return Ok(totalTempoMedioViagem);
        }

        private void WaitNSeconds(int seconds) // Função auxiliar que espera a execução da aplicação (sem interromper/travar) pelo número de segundos parâmetrizados
        {
            DateTime _desired = DateTime.Now.AddSeconds(seconds);
            while (DateTime.Now < _desired)
            {
                Thread.Sleep(1);
                System.Windows.Forms.Application.DoEvents();
            }
        }
    }
}