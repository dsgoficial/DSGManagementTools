#!/bin/bash

#configuring postgresql network--------------------------------------------
function alter_postgres_password() {
	export PGPASSWORD=$1
	psql -c "ALTER USER postgres WITH PASSWORD '$2'" -U postgres -h localhost -p 5432
}

echo "Alterar senha do usuário Postgres? (s/n)"; read alterarsenha
alterarsenha="${alterarsenha:=s}"
if [[ $alterarsenha == [sS] ]]; then
	echo "Entre com o password atual: "; read PASSWORD
	echo "Entre com o novo password: "; read NEWPASSWORD
		alter_postgres_password $PASSWORD $NEWPASSWORD
fi
#----------------installing and configuring packages--------------------------------------------

exit