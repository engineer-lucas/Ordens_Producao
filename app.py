#BACK-END FLASK: ROTAS DA API REST
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import init_bd, get_connection

#Cria uma instância da aplicação Flash
app = Flask(__name__, static_folder='static', static_url_path='')

#Habilitar os CORS
CORS(app)

#ROTA N1 - PÁGINA INICIAL ------------------------------------------
@app.route('/')
def index():
    #ALIMENTAR O ARQUIVO INDEX.HTML DA PASTA STATIC
    return app.send_static_file('index.html')
#ROTA N2 - STATUS API
@app.route('/status')
def status():
    """ROTA DE VERIFICAÇÃO DA API(SAÚDE)
    RETORNAR UM JSON INFORMANDO QUE O SERVIDOR ESTA 
    ATIVO"""
    return jsonify({
        "status": "online",
        "sistema": "Sistema de ordem de Produção",
        "versao":"1.0.0",
        "mensagem":"Ola, Fabrica, API FUNCIONANDO!"
    })
#ROTA N3 - LISTAR TODAS AS ORDENS(GET) -----------------------------
@app.route('/ordens', methods=['GET'])
def listar_ordens():
    """
    LISTAR TODAS AS ORDENS DE PRODUÇÃO CADASTRADAS.
    MÉTODOS HTTP: GET
    URL: http://localhost:5000/ordens
    Retorna: Lista e ordens em formato JSON.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ordens ORDER BY id DESC')
    ordens = cursor.fetchall()
    conn.close()
    #Converte cada Row do SQLite em discionario Python para serializar em JSON    
    return jsonify([dict(o) for o in ordens])

# ROTA POR ID - BUSCAR UMA ORDEM ESPECIFICA PELO ID(GET) -----------------

@app.route('/ordens/<int:ordem_id>', methods=['GET'])

def buscar_ordem(ordem_id):
    """
    Buscar uma única ordem de produção pelo ID.
    
    Parametros de URL:
        - ordem id(int): ID da ordem a ser buscada.
        
    Retornar:
        200 + JSON da ordem, se for encontrada.
        404 + mensagem de erro, se não existir.
    """
    conn = get_connection()
    cursor = conn.cursor()
    #o '?' é substituido pelo valor de ordem_id de forma segura
    cursor.execute('SELECT * FROM ordens WHERE id = ?', (ordem_id,))
    ordem = cursor.fetchone()  #ele rotorna um único registro ou None
    conn.close()
    
    if ordem is None:
        return jsonify({'erro': f'Ordem {ordem_id} nao encontarada.'}), 404
    return jsonify(dict(ordem)), 200


# ROTA : CRIAR NOVA ORDEM DE PRODUÇÃO (POST)----------------------------
@app.route('ordens', methods=['POST'])
def criar_ordem():
    """
    Cria uma nova ordem de produção a partir dos dados JSON enviados.
    
    Body esperado(JSON):
    
        produto      (str) : Nome do produto     - Obrigatório
        quantidade   (int) : Quantidade de peças - Obrigatório, > 0
        status       (str) : Opcional            - Padrão : 'Pendente'
    
    Retorno:
        201 : JSON da ordem criada, em caso de sucesso.
        400 : mensagem de erro, se dados inválidos
    """

    dados = request.get_json()
    
    if not dados:
        return jsonify({'erro': 'Body da requisicao ausente ou invalido'}), 400
    
    #verificação de campo obrigatório (produto)
    produto = dados.get('produto', '').strip()
    if not produto:
        return jsonify({'erro': 'Campo "Produto" e obrigatorio e nao pode ser vazio.'}), 400
    #verificação de campo obrigatório (quantidade)
    quantidade = dados.get('quantidade')
    if quantidade is None:
        return jsonify({'erro': 'Campo "quantidade" e obrigatorio.'}), 400
    #Verifica se a quantidade é um número inteiro e positivo
    try:
        quantidade = int(quantidade)
        if quantidade <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({'erro': 'Campo "Quantidade" deve ser um numero inteiro e positivo.'}), 400
    #Status (*pendente, em andamento, concluída) - opcional
    status_validos = ['Pendente','Em andamento','Concluida']
    status = dados.get('status', 'Pendente')
    if status not in status_validos:
        return jsonify({'erro': f'Status invalido. Use {status_validos}'}), 400
#PONTO DE PARTIDA -------------------------------------------------------

if __name__=='__main__':
    init_bd()
    
    app.run(debug=True, host='0.0.0.0', port=5000)


