import unittest
import os
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extractor import extrair_estrutura

class TestDatabaseExtractor(unittest.TestCase):
    
    def setUp(self):
        self.catalogo = extrair_estrutura()

    def test_estrutura_raiz(self):
        """Testa se as chaves principais do JSON estão corretas"""
        self.assertEqual(self.catalogo.get("database"), "agora")
        self.assertEqual(self.catalogo.get("schema"), "agora")
        self.assertIsInstance(self.catalogo.get("tables"), list)

    def test_tabelas_esperadas_existem(self):
        """Testa se as tabelas listadas na issue foram encontradas"""
        tabelas_extraidas = [t["name"] for t in self.catalogo["tables"]]
        tabelas_esperadas = [
            "remuneracoes",
            "servidores_tlp",
            "unidades_tlp",
            "unidades_tlp_cargos_funcoes",
            "rubricas_folha"
        ]
        
        for tabela in tabelas_esperadas:
            self.assertIn(tabela, tabelas_extraidas)

    def test_estrutura_tabela(self):
        """Testa se a tabela remuneracoes possui as chaves corretas"""
        tabela = next((t for t in self.catalogo["tables"] if t["name"] == "remuneracoes"), None)
        self.assertIsNotNone(tabela)
        
        self.assertIn("columns", tabela)
        self.assertIn("primary_key", tabela)
        self.assertIn("foreign_keys", tabela)
        
        self.assertIsInstance(tabela["primary_key"], list)
        self.assertIsInstance(tabela["foreign_keys"], list)

if __name__ == '__main__':
    unittest.main()