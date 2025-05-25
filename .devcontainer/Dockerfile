FROM ghcr.io/ipspace/netlab/devcontainer:2.0.1

# Add vscode user to clab_admins group
RUN sudo usermod -aG clab_admins vscode

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.7.8 /uv /uvx /bin/

CMD ["bash"]
