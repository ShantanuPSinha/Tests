apt update && apt install -y git default-jdk python3 python3-pip wget curl tar
mkdir tools

pushd tools

# Install Maven
wget -O - https://dlcdn.apache.org/maven/maven-3/3.9.6/binaries/apache-maven-3.9.6-bin.tar.gz | tar xzf -
export PATH=$PWD/apache-maven-3.9.6/bin:$PATH

# Install NVM
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
nvm install --lts
nvm use --lts

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

popd

git clone https://github.com/rongpan/RFixer.git

pushd RFixer

mvn install
export LD_LIBRARY_PATH=$PWD:$LD_LIBRARY_PATH