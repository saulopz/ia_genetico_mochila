import sys
import json
from random import *


# ITEM CLASS ---------------------------------------------
# representa os itens do arquivo config.json
class Item:
    def __init__(self, name, value, weight):
        self.name = name        # nome do produto
        self.value = value      # valor
        self.weight = weight    # peso


# DATA STATIC CLASS ------------------------------------
# Lê as configurações do arquivo config.json e carrega
# nessa classe estática para ser usada em todo o programa
class Data:
    # Coloquei aqui a configuração das variáveis para ajustes do algoritmo
    # genético no arquivo json de configuração e leio elas em Data
    population_size = 50            # tamanho da população
    selection_size = 20             # quantos vou selecionar
    crossover_gene_size = 2         # quantos gens vou usar no cruzamento
    mutation_individual_size = 10   # quantos indivíduos vou mutar cada geração
    mutation_gene_size = 2          # quantos gens de cada indivíduo vou mutar
    penality = 100                  # desconto de penalidade ao passar do peso
    generations = 100               # por quantas gerações o algoritmo vai executar

    size = 0        # quantidade de itens
    capacity = 0    # capacidade da mochila
    items = []      # vetor contendo os itens

    @staticmethod
    def load(filename):
        # abre o arquivo e converte para um objeto json
        file = open(filename)
        data = json.load(file)
        file.close()

        # coloca as informações do objeto json na classe
        # Data pra facilitar o acesso aos dados
        Data.population_size = int(data["population_size"])
        Data.selection_size = int(data["selection_size"])
        Data.crossover_gene_size = int(data["crossover_gene_size"])
        Data.mutation_individual_size = int(data["mutation_individual_size"])
        Data.mutation_gene_size = int(data["mutation_gene_size"])
        Data.generations = int(data["generations"])

        Data.capacity = int(data["capacity"])
        for i in range(len(data["items"])):
            name = data["items"][i]["name"]
            value = int(data["items"][i]["value"])
            weight = int(data["items"][i]["weight"])
            Data.items.append(Item(name, value, weight))
            Data.size += 1


# INDVIDUAL CLASS -------------------------------------------
# Cada instância dessa classe representa cada indivíduo da
# população do ecossistema do algoritmo
class Individual:
    def __init__(self):
        self.fitness = 0                # aptidão do indivíduo
        self.accumulated_fitness = 0    # aptidão acumulada (usada na seleção)
        self.selected = False           # se indivíduo foi selecionado
        self.gene = []                  # gens, representando os ítens na mochiila
        for i in range(Data.size):
            # coloca ítens aleatórios na mochila
            self.gene.append(randint(0, 1))

    # Calcula a aptidão do indivíduo
    def evaluate(self):
        self.accumulated_fitness = 0
        self.fitness = 0
        weight = 0
        # primeiro soma todos os valores dos ítens que estão inclusos
        # nessa solução de mochila
        for i in range(Data.size):
            if self.gene[i] == 1:
                self.fitness += Data.items[i].value
                weight += Data.items[i].weight
        # caso o peso total de ítens incluso seja maior que a capacidade
        # da mochila, dá uma penalidade, diminuindo em 100 a aptidão
        if weight > Data.capacity:
            self.fitness -= Data.penality

    # apresenta informações do indivíduo de forma simplificada para debug
    def show(self):
        print(self.gene, self.fitness, self.selected, self.accumulated_fitness)

    # apresenta informações completas da solução, representada por um indivíduo
    def show_info(self):
        print("SOLUÇÃO ------------------------------")
        print("Capacidade da mochila:", Data.capacity)
        weight = 0
        value = 0
        for i in range(Data.size):
            if self.gene[i] == 1:
                weight += Data.items[i].weight
                value += Data.items[i].value
                print("-", Data.items[i].name, "valor:",
                      Data.items[i].value, "gold - peso:", Data.items[i].weight)
        print("Valor total:", value, "gold")
        print("Peso total :", weight)
        print("--------------------------------------")

    # clona o indivíduo e retorna uma instância dessa cópia
    def clone(self):
        other = Individual()
        for i in range(Data.size):
            other.gene[i] = self.gene[i]
        other.fitness = self.fitness
        return other


# GENETIC CLASS --------------------------------------------------
class Genetic:
    # constructor
    def __init__(self):
        self.population = []    # inicia com população vazia

    # mostra todos os indivíduos da população
    def show(self):
        for i in self.population:
            i.show()

    # cria a população inicial com indivíduos contendo ítens aleatórios
    def create_population(self):
        print("CREIANDO POPULAÇÃO INICIAL...")
        for i in range(Data.population_size):
            self.population.append(Individual())

    # calcula a aptidão de todos os indivíduos da população
    def evaluate(self):
        for i in self.population:
            i.evaluate()
        # ordena a população com base na aptidão
        self.population.sort(key=lambda x: x.fitness)

    # seleciona uma quantidade de indivíduos. Se best for verdadeiro,
    # então seleciona os melhores, se for falso, seleciona os piores.
    def selection(self, best):
        who = "MELHORES"
        if not best:
            who = "PIORES"
        print("SELECIONANDO OS", who, "INDIVÍDUOS ...")
        # como para fins de cálculo não pode haver aptidão negativa,
        # procura a menor aptidão negativa para subtrair de todos,
        # deixando todos positivos.
        lower = 0
        for i in self.population:
            if i.fitness < lower:
                lower = i.fitness

        # Se houve aptidão negativa, subtrai o menor valor de
        # todos os elementos para não termos aptidão negativa
        if lower < 0:
            for i in self.population:
                i.fitness = i.fitness - lower

        # ordena a população com base na aptidão
        self.population.sort(key=lambda x: x.fitness)

        # calcula a aptidão acumulada e aptidão total
        fitness_total = 0
        for i in self.population:
            fitness_total += i.fitness
            i.accumulated_fitness = fitness_total

        # se é pra selecionar os piores, inverte o aptidão
        # acumulada e ordena novamente pela aptidão acumulada
        # assim, os piores tem mais chances de serem escolhidos
        if not best:
            # Inverte as probabilidades. Os piores vão ganhar uma
            # porção maior na roleta e os melhores menor
            size = len(self.population)
            for i in range(int(size / 2)):
                a = self.population[i]
                b = self.population[size - 1 - i]
                aux = a.accumulated_fitness
                a.accumulated_fitness = b.accumulated_fitness
                b.accumulated_fitness = aux
            self.population.sort(key=lambda x: x.accumulated_fitness)

        # Sempre seleciono os dois mais fortes, para garantir que eles
        # se reproduzam e não morram
        if best:
            self.population[-1].selected = True
            self.population[-2].selected = True
        else:
            self.population[0].selected = True
            self.population[1].selected = True

        # e roda a roleta para selecionar a quantidade de indivúdios
        # definida em Data.selection_size
        for j in range(Data.selection_size - 2):
            # pega um número aleatório com base na aptidão total
            num = randint(0, fitness_total)
            last = 0
            i = 0
            found = False
            # enquanto não encontrou um indivíduo que tem a ficha
            # desse número, procura
            while not found:
                current = self.population[i].accumulated_fitness
                # se encontrou o felizardo (ou não)
                if last <= num <= current:
                    # se já está selecionado, pega o próximo não
                    # selecionado da roleta
                    while self.population[i].selected:
                        # se chegou ao final, volta para o início
                        # veja que está girando a roleta e é circular
                        i += 1
                        if i >= len(self.population):
                            i = 0
                    # achou um indivíduo seleciona ele
                    self.population[i].selected = True
                    found = True
                last = current
                i += 1

    # faz o cruzamento dos indivíduos selecioados
    def crossover(self):
        print("CRUZAMENTO...")
        # cria uma lista para os selecionados. Fica mais fácil.
        selected = []
        for i in self.population:
            if i.selected:
                selected.append(i)
                # já deseleciona os pais
                i.selected = False
        # randomiza para fazer pares aleatórios
        shuffle(selected)
        i = 0
        # vai seguindo a lista dos selecionados pegando os dois
        # primeiros, depois os dois seguintes e assim por diante
        while i < len(selected):
            child_a = selected[i].clone()
            child_b = selected[i+1].clone()
            for j in range(Data.crossover_gene_size):
                # escolhe um gen aleatório e troca nos filhos
                k = randint(0, Data.size - 1)
                child_a.gene[k] = selected[i+1].gene[k]
                child_b.gene[k] = selected[i].gene[k]
            # coloca os filhos na lista da população
            self.population.append(child_a)
            self.population.append(child_b)
            i += 2

    # Faz a mutação de alguns indivíduos escolhidos aleatoriamente.
    def mutation(self):
        print("MUTAÇÃO...")
        # pega uma quantidade aleatória de indivíduos para mutar
        # a cada geração, entre 0 e Data.mutation_individual_size
        size = randint(0, Data.mutation_individual_size)
        for i in range(size):
            # pega um indivíduo aleatório da população
            k = randint(0, len(self.population) - 1)
            # pega alguns gens aleatórios e inverte o valor
            for j in range(Data.mutation_gene_size):
                l = randint(0, Data.size - 1)
                if self.population[k].gene[l] == 1:
                    self.population[k].gene[l] = 0
                else:
                    self.population[k].gene[l] = 1

    # Depois de selecionar os piores indivíduos, mas com
    # possibilidades de alguns bons serem selecionados na
    # roleta, mata esses selecionados, deixando apenas os
    # "melhores" para a próxima geração
    def survival(self):
        print("SOBREVIVENTES...")
        aux = []
        for i in self.population:
            if not i.selected:
                aux.append(i)
        self.population = aux

    # Algoritmo genético propriamente dito.
    def run(self):
        self.create_population()
        for g in range(Data.generations):
            print("GERAÇÃO", g)
            self.evaluate()
            self.selection(True)
            self.show()
            self.crossover()
            self.mutation()
            self.evaluate()
            self.selection(False)
            self.show()
            self.survival()
        self.evaluate()
        self.show()
        self.population[-1].show_info()


# MAIN PROGRAM -----------------------------------------
def main():
    # carrega as configurações do arquivo passado como parâmetro
    Data.load(sys.argv[1])
    # inicio o algoritmo
    genetic = Genetic()
    genetic.run()


# -------------------------------------------------------
if __name__ == "__main__":
    main()
