receita = float(input('Informe o valor da Receita (DRE) em R$ '))
custo = float(input('Informe o valor do custo (DRE) em R$ '))
estoques = float(input('Informe o valor dos estoques (Balanço) em R$ '))
clientes = float(input('Informe o valor das contas a receber (Balanço) em R$ '))
fornecedores = float(input('Informe o valor dos fornecedores (Balanço) em R$ '))
tempo = int(input('Informe o número de dias do tempo do balanço '))
pme = (estoques / custo) * tempo
pmr = (clientes / receita) * tempo
pmp = (fornecedores / custo) * tempo
co = pme + pmr
cc = co - pmp
print(f'O prazo médio de estoques - PME é {pme:.0f} dias')
print(f'O prazo médio de recebimento - PMR é {pmr:.0f} dias')
print(f'O prazo médio de pagamento - PMP é {pmp:.0f} dias')
print(f'O ciclo operacional - CO é {co:.0f} dias')
print(f'O ciclo de caixa - CC é {cc:.0f} dias')
if cc > 0:
  print(f'O CC indica que a empresa paga em média {cc:.0f} dias antes de receber')
else:
  print(f'O CC indica que a empresa recebe em média {cc:.0f} dias antes de pagar')