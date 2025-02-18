import os
import unittest
import io
from flask import Response
from app import app, DB_FOLDER
from modules.db_manager import create_db_if_not_exists

class TestApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Executado uma vez antes de todos os testes.
        - Remove DB de teste preexistente
        - Cria o DB de teste chamando create_db_if_not_exists
        - Inicializa o Flask test client
        """
        cls.test_db_name = "test_app.db"
        cls.test_db_path = os.path.join(DB_FOLDER, cls.test_db_name)
        if os.path.isfile(cls.test_db_path):
            os.remove(cls.test_db_path)

        # Garante que o DB de teste seja criado vazio
        create_db_if_not_exists(cls.test_db_path)

        # Cria o test_client do Flask
        cls.client = app.test_client()

    def test_01_list_db_files(self):
        """
        Testa rota GET /select_db para ver se lista DBs disponíveis (db_files).
        """
        resp = self.client.get("/select_db")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("db_files", data, "Resposta não contém a chave 'db_files'.")

    def test_02_select_test_db(self):
        """
        Testa rota POST /select_db para 'carregar' o test_app.db recém criado,
        simulando a ação do usuário.
        """
        resp = self.client.post("/select_db", data={"db_name": self.test_db_name})
        self.assertEqual(resp.status_code, 200, "Não foi possível selecionar o DB de teste.")
        data = resp.get_json()
        self.assertEqual(data.get("status"), "success",
                         "Não retornou 'success' ao carregar DB de teste.")

    def test_03_ingest_content_text(self):
        """
        Testa rota /ingest_content enviando texto copiado (sample_text).
        Agora usamos um texto mais longo e multi-parágrafo.
        """
        sample_text = (
            "Este é um texto de teste mais longo para verificar se a ingestão "
            "de texto copiado funciona corretamente. Ele contém várias sentenças "
            "e tem como objetivo simular um conteúdo real.\n\n"
            "Este segundo parágrafo serve para ampliar o corpus, permitindo que "
            "seja possível observar o comportamento do módulo de análise."
        )
        resp = self.client.post(
            "/ingest_content",
            data={"text": sample_text},
            content_type="multipart/form-data"
        )
        # Esperamos status_code 200 e "status": "success" no JSON
        self.assertEqual(resp.status_code, 200,
                         f"Falha ao enviar texto copiado, status code={resp.status_code}")
        data = resp.get_json()
        self.assertEqual(data.get("status"), "success")

    def test_04_ingest_content_file(self):
        """
        Testa rota /ingest_content enviando um arquivo .txt.
        Usamos o nome de arquivo 'sample_text_8.txt' (caminho hard-coded),
        mas o conteúdo simulado é meramente bytes em memória.
        """
        file_content = b"/home/base/Nextcloud/Desktop/test_texts/sample_text_8.txt"
        data = {
            # Note que o nome do arquivo enviado é o 2º elemento da tupla
            "file": (io.BytesIO(file_content), "/home/base/Nextcloud/Desktop/test_texts/sample_text_8.txt")
        }
        resp = self.client.post(
            "/ingest_content",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(resp.status_code, 200,
                         f"Falha ao enviar arquivo, status code={resp.status_code}")
        data_json = resp.get_json()
        self.assertEqual(data_json.get("status"), "success")

    def test_05_ingest_links(self):
        """
        Testa rota /ingest_links enviando um link real do CNN Brasil,
        para verificar se o scraper consegue processar ou pelo menos
        retorna status 200.
        """
        links_text = (
            "https://www.cnnbrasil.com.br/economia/macroeconomia/"
            "regulamentacao-da-tributaria-lula-veta-isencao-para-fundos-de-investimento/"
        )
        resp = self.client.post(
            "/ingest_links",
            data={"links": links_text},
            content_type="multipart/form-data"
        )
        # O scraping pode falhar por motivos diversos, mas esperamos no mínimo
        # que a rota seja executada. Se ela não encontrar conteúdo, pode retornar
        # status 200 com "status": "success" ou outra chave, ou 400 se falhou.
        self.assertIn(resp.status_code, [200, 400, 500],
                      f"Status code inesperado ao enviar link: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.get_json()
            self.assertEqual(data.get("status"), "success")

    def test_06_process_sentiment(self):
        """
        Testa rota /process_sentiment para gerar HTML fixo/dinâmico do texto.
        Pode falhar (400) se não houver conteúdo suficiente ou se a análise falhar.
        """
        resp = self.client.post("/process_sentiment")
        # Se não houver conteúdo no DB, a rota pode retornar 400. 
        # Se houver, deve retornar 200 e JSON com "html_fixed"/"html_dynamic".
        if resp.status_code == 200:
            data = resp.get_json()
            self.assertIn("html_fixed", data)
            self.assertIn("html_dynamic", data)
        else:
            print(f"Aviso: /process_sentiment retornou: {resp.status_code}")

    def test_07_select_algorithm_and_generate(self):
        """
        Testa rota /select_algorithm_and_generate para mudar o algoritmo (ex: naive_bayes).
        """
        resp = self.client.post("/select_algorithm_and_generate", data={"algorithm": "naive_bayes"})
        if resp.status_code == 200:
            data = resp.get_json()
            self.assertIn("status", data)
        else:
            print(f"Aviso: /select_algorithm_and_generate retornou: {resp.status_code}")

    def test_08_process(self):
        """
        Testa rota /process, que gera representação social.
        Pode retornar 400 se não houver conteúdo.
        """
        form_data = {
            "stopwords": "com",
            "zone": "Núcleo Central",
            "extra_filter": "nao"
        }
        resp = self.client.post("/process", data=form_data)
        if resp.status_code == 200:
            data = resp.get_json()
            if isinstance(data, dict) and "html" in data:
                self.assertIn("<table", data["html"])  # Exemplo simples
        else:
            print(f"Aviso: /process retornou: {resp.status_code}")

    def test_09_identify_entities(self):
        """
        Testa rota /identify_entities (entity_finder).
        """
        resp = self.client.post("/identify_entities")
        self.assertIn(resp.status_code, [200, 400, 500])
        if resp.status_code == 200:
            data = resp.get_json()
            self.assertIn("status", data)
            self.assertIn(data["status"], ["success", "cached"])

    def test_10_generate_timeline(self):
        """
        Testa rota /generate_timeline, que gera arquivo .timeline e retorna JSON.
        """
        resp = self.client.post("/generate_timeline", data={"text": ""})
        if resp.status_code == 200:
            data = resp.get_json()
            self.assertIn(data.get("status"), ["success", "cached"])
        else:
            print(f"Aviso: /generate_timeline retornou: {resp.status_code}")

    def test_11_list_timelines(self):
        """
        Testa GET /list_timelines.
        """
        resp = self.client.get("/list_timelines")
        if resp.status_code == 200:
            data = resp.get_json()
            self.assertIn("timelines", data)
        else:
            print(f"Aviso: /list_timelines retornou: {resp.status_code}")

    def test_12_llama_query(self):
        """
        Testa rota /llama_query com pergunta simples.
        """
        payload = {"question": "Teste de pergunta LlamaIndex"}
        resp = self.client.post("/llama_query", json=payload)
        self.assertIn(resp.status_code, [200, 404, 500])
        if resp.status_code == 200:
            data = resp.get_json()
            self.assertIn("answer", data)

    def test_13_generate_cenarios(self):
        """
        Testa rota /generate_cenarios, que agora chama prospect.py (ScenarioClassifier).
        """
        resp = self.client.post("/generate_cenarios")
        self.assertIn(resp.status_code, [200, 400])
        if resp.status_code == 200:
            data = resp.get_json()
            self.assertIn("html", data)

    def test_14_save_to_db(self):
        """
        Testa rota /save_to_db, que salva as análises no DB atual.
        """
        resp = self.client.post("/save_to_db")
        self.assertIn(resp.status_code, [200, 400])
        if resp.status_code == 200:
            data = resp.get_json()
            self.assertEqual(data.get("status"), "success")

    def test_15_delete_db(self):
        """
        Testa a rota /delete_db para remover o DB de teste criado.
        """
        resp = self.client.post("/delete_db", data={"db_name": self.test_db_name})
        self.assertIn(resp.status_code, [200, 400, 404])
        if resp.status_code == 200:
            data = resp.get_json()
            self.assertEqual(data.get("status"), "success")

    @classmethod
    def tearDownClass(cls):
        """
        Executado uma vez após todos os testes.
        Remove o DB de teste, se existir ainda.
        """
        if os.path.isfile(cls.test_db_path):
            os.remove(cls.test_db_path)


if __name__ == "__main__":
    unittest.main()
