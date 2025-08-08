module.exports = {
    branches: [
        'main',               // releases estáveis
        { name: 'Dev', prerelease: true }, // pre-releases ex.: 1.2.0-dev.1
    ],
    plugins: [
        ['@semantic-release/commit-analyzer', { preset: 'conventionalcommits' }],
        ['@semantic-release/release-notes-generator', { preset: 'conventionalcommits' }],
        ['@semantic-release/changelog', { changelogFile: 'CHANGELOG.md' }],
        // Atualiza apenas o version do frontend; não publica no npm
        ['@semantic-release/npm', { npmPublish: false, pkgRoot: 'frontend' }],
        ['@semantic-release/github', { assets: [] }],
        ['@semantic-release/git', {
            assets: ['CHANGELOG.md', 'frontend/package.json'],
            message: 'chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}'
        }],
    ],
};
