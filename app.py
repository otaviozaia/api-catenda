from flask import Flask
from flask import jsonify, request, render_template
import json
import requests
 
app = Flask(__name__)

#no ambiente tenda será colocada uma rota de requisição para nossa API com o token de sessão do usuário e seu community-id
#/push-key?token=TOKEN&community=COMMUNITY
@app.route("/push-key",methods=['GET'])#rota que será colocada no tenda para requisição na nossa api, o que está entre "<>" são variáveis
def getDados():
    token = request.args.get("token")
    community = request.args.get("community")
    #armazenará resposta final
    datas = None
    #armazenará os alias e nomes existentes no json inserido em 'datas'
    raS = []
    names = []
    #armazenará os cursos(disciplinas) e médias por aluno
    studentScores = []



    api_url_base = 'https://api.edu.test.tenda.digital/v1' #rota padrão para todas as requisições feitas à API do tenda
    #os headers são recebidos na rota pelas variáveis token e community
    headers1 = {'community-id':community,
               'Content-type':'application/json',
               'Authorization':'Bearer {0}'.format(token)}
    
    #definindo rota de requisição para a API do tenda. */use/me? é utilizada para recuperar todas as informações sobre um usuário
    api_url = '{0}/user/me?'.format(api_url_base)

    #a variável responde guardará o retorno da requisição feita ao tenda
    response = requests.get(api_url,headers=headers1)

    # variável datas recebe resultado do response em json
    datas = json.loads(response.content)

    #escolhemos os itens que queremos retornar dentro do json, aqui no caso o alias (identificador (no menu contas) e ID (ID quando for registrar aluno no menu alunos)) * obs: alias seria o RA
    #alias =  datas['members'][0]['alias']

    #armazeno na variável array todos os alias de alunos associados à conta 'familiar' 
    if raS == []:
        for i in range(len(datas['members'])):
            raS.append(datas['members'][i]['alias'])

    if names == []:
        for name in range(len(datas['members'])):
            names.append(datas['members'][name]['name'])

    #testando retorno para ver se realmente foram armazenados os alias no array
    #return array[0]+' '+array[1]
    #armazenará o json final para posteriormente ser incluído o front em cima das informações
    coursesInformations = []

    #varrerá os ra´s dentro de array para fazer a requisição para a api do canvas e coletar dados baseado nos 'alias'(ra)
    for ra in raS:
        #url que extrai dados de todos os cursos que o aluno está inserido
        url = 'https://veredaeducacao.test.instructure.com/api/v1/users/sis_user_id:'+ra+'/courses.json?include[]=total_scores&enrollment_state=active'
            
        headers2 = {'Content-type': 'application/json',
           'Authorization': 'Bearer <token api canvas>'}


        response2 = requests.get(url,headers=headers2)

        #se não retornar uma resposta válida, os campos notas ficam vazios
        if response2.status_code >= 200 and response2.status_code < 300:
            coursesInformations.append(json.loads(response2.content))

        #ambos abaixo retornam a resposta da requisição acima, porém para desmembrar os itens do json, usamos o json.loads
        #coursesInformations.append(json.loads(response2.content))
        #coursesInformations.append(response2.content)
    
    if studentScores == []:
            #para cada índice (que indica 1 aluno) no coursesInformations:
            for student in range(len(coursesInformations)):
                #lista de médias de aluno adiciona 1 índice que corresponderá ao aluno do couresInformations
                studentScores.append([])
                #no json do coursesInformations, há uma lista de dicionários (cada dicionário é 1 curso) e suas respectivas informações
                for course in range(len(coursesInformations[student])):
                    #armazena o nome do curso
                    name = coursesInformations[student][course]['name']
                    #armazena a média do curso
                    if coursesInformations[student][course]['enrollments'][0]['unposted_current_score'] == None:
                        score = 0.0
                    else:
                        score = coursesInformations[student][course]['enrollments'][0]['unposted_current_score']
                    #cria um dicionário com nome do curso e média e adiciona ao primeiro índice (primeiro aluno) na lista de médias por aluno (studentScores)
                    studentScores[student].append({'name':name,'score':score})
            

    #testando retornos armazenados
    #return coursesInformations[0][0]['name'] 
    #return str(coursesInformations[0][0]['enrollments'][0]['unposted_final_score'])
    #return coursesInformations[0] // consulta o json inteiro, porém a variavel tem que receber o conteúdo da segunda maneira citada acima no código
    #return studentScores[0][0]['score']

    return render_template('index.html',names=names,raS=raS,studentScores=studentScores)

#roda servidor local
if __name__ == '__main__':
    app.run(debug=False)




